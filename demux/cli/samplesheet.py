""" CLI points for samplesheeet action """
import copy
import click
import csv
import logging
import sys

from pathlib import Path
from typing import List, Dict

from cglims.api import ClinicalLims
from demux.exc import NoValidReagentKitFound

from ..utils import (
    Create2500Samplesheet,
    CreateNovaseqSamplesheet,
    HiSeq2500Samplesheet,
    HiSeqXSamplesheet,
    MiseqSamplesheet,
    NIPTSamplesheet,
    Samplesheet,
)

LOG = logging.getLogger(__name__)


@click.group()
def sheet():
    """Samplesheet commands"""
    pass


@sheet.command()
@click.argument("samplesheet")
@click.option(
    "-a",
    "--application",
    type=click.Choice(["wgs", "wes", "nipt", "miseq"]),
    help="sequencing type",
)
def validate(samplesheet, application):
    """validate a samplesheet"""
    if application == "nipt":
        NIPTSamplesheet(samplesheet).validate()
    elif application == "wes":
        HiSeq2500Samplesheet(samplesheet).validate()
    elif application == "miseq":
        MiseqSamplesheet(samplesheet).validate()
    elif application == "wgs":
        HiSeqXSamplesheet(samplesheet).validate()


@sheet.command()
@click.argument("samplesheet")
def massage(samplesheet):
    """create a NIPT ready SampleSheet"""
    click.echo(NIPTSamplesheet(samplesheet).massage())


@sheet.command()
@click.argument("samplesheet", type=str)
@click.argument("sample", type=str)
def sample_in_pooled_lane(samplesheet: str, sample: str) -> None:
    """Check if a sample is in a pooled lane"""
    sample_sheet = Samplesheet(samplesheet)

    if not any([sample == seq_sample for seq_sample in sample_sheet.samples()]):
        LOG.error(f"{sample} not in {samplesheet}")
        raise click.Abort()
    if sample_sheet.sample_in_pooled_lane(sample):
        click.echo("true")
    else:
        click.echo("false")


@sheet.command()
@click.argument("samplesheet")
@click.option(
    "-a", "--application", type=click.Choice(["miseq", "nipt"]), help="sequencing type"
)
@click.option("-f", "--flowcell", help="for miseq, please provide a flowcell id")
def demux(samplesheet, application, flowcell):
    if application == "nipt":
        """convert NIPT samplesheet to demux'able samplesheet """
        click.echo(NIPTSamplesheet(samplesheet).to_demux())
    elif application == "miseq":
        """convert MiSeq samplesheet to demux'able samplesheet """
        click.echo(MiseqSamplesheet(samplesheet, flowcell).to_demux())
    else:
        LOG.error("No application provided!")
        sys.exit(1)


@sheet.command()
@click.argument("flowcell")
@click.option(
    "-a",
    "--application",
    type=click.Choice(["wgs", "wes", "nova", "iseq"]),
    help="application type",
)
@click.option(
    "-i",
    "--dualindex",
    is_flag=True,
    default=False,
    help="X: force dual index, not used \
              for NovaSeq!",
)
@click.option(
    "-l",
    "--index-length",
    default=None,
    help="2500 and NovaSeq: only return this index length",
)
@click.option(
    "-L", "--longest", is_flag=True, help="2500 and NovaSeq: only return longest index"
)
@click.option(
    "-S",
    "--shortest",
    is_flag=True,
    help="2500 and NovaSeq: only return shortest index",
)
@click.option(
    "-d", "--delimiter", default=",", show_default=True, help="column delimiter"
)
@click.option("-e", "--end", default="\n", show_default=True, help="line delimiter")
@click.option(
    "-p",
    "--pad",
    is_flag=True,
    default=False,
    help="add 2 bases to indices with length 8",
)
@click.pass_context
def fetch(
    context,
    flowcell,
    application,
    dualindex,
    index_length,
    longest,
    shortest,
    pad,
    delimiter=",",
    end="\n",
):
    """
    Fetch a samplesheet from LIMS.
    If a flowcell has dual indices of length 10+10 bp (dual 10) and/or 8+8 bp (dual 8), use
    the option -p, or --pad to add two bases to length 8 indices (AT for index1, AC for index2).
    This will ensure that all indices in the sample sheet are of the same length, namely 10.
    """

    def reverse_complement(dna):
        complement = {"A": "T", "C": "G", "G": "C", "T": "A"}
        return "".join([complement[base] for base in dna[::-1]])

    def get_project(project):
        """ Only keeps the first part of the project name"""
        return project.split(" ")[0]

    if application == "nova":
        lims_config = context.obj["lims"]
        dummy_indexes = context.obj["dummy_indexes"]
        runs_dir = context.obj["runs_dir"]["novaseq"]

        try:
            demux_samplesheet = CreateNovaseqSamplesheet(
                dummy_indexes,
                flowcell,
                lims_config,
                pad,
                runs_dir,
            ).construct_samplesheet()

            # add [section] header
            click.echo("[Data]")
            click.echo(demux_samplesheet)
            return
        except NoValidReagentKitFound as error:
            LOG.error(error.message)
            raise click.Abort()

    lims_api = ClinicalLims(**context.obj["lims"])
    raw_samplesheet = list(lims_api.samplesheet(flowcell))

    if len(raw_samplesheet) == 0:
        sys.stderr.write(f"Samplesheet for {flowcell} not found in LIMS! ")
        context.abort()

    if longest:
        longest_row = max(
            raw_samplesheet, key=lambda x: len(x["index"].replace("-", ""))
        )
        index_length = len(longest_row["index"].replace("-", ""))

    if shortest:
        shortest_row = min(
            raw_samplesheet, key=lambda x: len(x["index"].replace("-", ""))
        )
        index_length = len(shortest_row["index"].replace("-", ""))

    # ... fix some 2500 specifics
    if application == "wes":
        demux_samplesheet = Create2500Samplesheet(
            flowcell, index_length, raw_samplesheet
        ).construct_samplesheet()

        # add [section] header
        click.echo("[Data]")
        click.echo(demux_samplesheet)
        return

    # ... fix some X specifics
    if application == "wgs":
        if dualindex:
            lims_keys = [
                "fcid",
                "lane",
                "sample_id",
                "sample_ref",
                "index",
                "index2",
                "sample_name",
                "control",
                "recipe",
                "operator",
                "project",
            ]
            for line in raw_samplesheet:
                line["index2"] = ""
        else:
            lims_keys = [
                "fcid",
                "lane",
                "sample_id",
                "sample_ref",
                "index",
                "sample_name",
                "control",
                "recipe",
                "operator",
                "project",
            ]

        header = [Samplesheet.header_map[head] for head in lims_keys]

        # first do some 10X magic, if any
        new_samplesheet = []
        for i, line in enumerate(raw_samplesheet):
            index = line["index"]
            if len(index.split("-")) == 4:
                for tenx_index in index.split("-"):
                    tenx_line = copy.deepcopy(line)
                    tenx_line["sample_id"] = "{}_{}".format(
                        line["sample_id"], tenx_index
                    )
                    tenx_line["index"] = tenx_index
                    new_samplesheet.append(tenx_line)
            else:
                new_samplesheet.append(line)
        raw_samplesheet = new_samplesheet

        # do some single/dual index stuff
        for i, line in enumerate(raw_samplesheet):
            if not dualindex:
                index = line["index"].split("-")[0]
                raw_samplesheet[i]["index"] = index
                raw_samplesheet[i]["sample_id"] = "{}_{}".format(
                    line["sample_id"], index
                )
            else:
                ori_index = line["index"]
                indexes = ori_index.split("-")
                if len(indexes) == 2:
                    (index1, index2) = indexes
                    raw_samplesheet[i]["index"] = index1
                    raw_samplesheet[i]["index2"] = reverse_complement(index2)
                    raw_samplesheet[i]["sample_id"] = "{}_{}".format(
                        line["sample_id"], ori_index
                    )

        # add [section] header
        click.echo("[Data]")

    click.echo(delimiter.join(header))
    for line in raw_samplesheet:
        # fix the project content
        project = get_project(line["project"])
        line["project"] = project
        line["sample_name"] = project

        # print it!
        click.echo(delimiter.join([str(line[lims_key]) for lims_key in lims_keys]))
