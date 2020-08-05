# -*- coding: utf-8 -*-
import click
import logging

from path import Path
import xml.etree.cElementTree as et

from .utils import (
    Samplesheet,
    HiSeqXSamplesheet,
    NIPTSamplesheet,
    HiSeq2500Samplesheet,
    MiseqSamplesheet,
)

log = logging.getLogger(__name__)


@click.group()
def basemask():
    """Samplesheet commands"""
    pass


@basemask.command()
@click.argument("rundir")
@click.option("-l", "--lane", help="lane number")
@click.option(
    "-a",
    "--application",
    type=click.Choice(["wgs", "wes", "nipt", "miseq", "nova"]),
    help="sequencing type",
)
def create(rundir, lane, application):
    """Create a basemask based on SampleSheet.csv and runParameters"""

    # runParameters.xml
    def parse_run_parameters(run_parameters_file):
        return et.parse(Path(rundir).joinpath(run_parameters_file))

    def create_basemask(run_params_tree, sheet):
        read1_len = int(run_params_tree.findtext("Setup/IndexRead1"))
        read2_len = int(run_params_tree.findtext("Setup/IndexRead2"))

        lines = [line for line in sheet.lines_per_column("lane", lane)]

        # get the index lengths
        index1 = lines[0]["index"]
        index2 = lines[0]["index2"] if "index2" in lines[0] else ""

        # index1 basemask
        i1n = "n" * (read1_len - len(index1))
        i1 = "I" + str(len(index1)) + i1n

        # index2 basemask
        if read2_len == 0:
            click.echo(f"Y151,{i1},Y151")
        else:
            i2n = "n" * (read2_len - len(index2))
            if len(index2) > 0:
                i2 = "I" + str(len(index2)) + i2n
            else:
                i2 = i2n
            click.echo(f"Y151,{i1},{i2},Y151")

    def create_novaseq_basemask(run_params_tree):
        indexread1 = int(run_params_tree.findtext("IndexRead1NumberOfCycles"))
        indexread2 = int(run_params_tree.findtext("IndexRead2NumberOfCycles"))
        read1 = int(run_params_tree.findtext("Read1NumberOfCycles"))
        read2 = int(run_params_tree.findtext("Read2NumberOfCycles"))

        basemask = f"Y{read1},I{indexread1},I{indexread2},Y{read2}"

        click.echo(f"{basemask}")

    sheet = None
    samplesheet = Path(rundir).joinpath("SampleSheet.csv")
    if application == "nipt":
        sheet = NIPTSamplesheet(samplesheet)
    elif application == "wes":
        sheet = HiSeq2500Samplesheet(samplesheet)
    elif application == "miseq":
        sheet = MiseqSamplesheet(samplesheet)
    elif application == "wgs":
        sheet = HiSeqXSamplesheet(samplesheet)

    if application == "nova":
        run_parameters_file = "RunParameters.xml"
        run_params_tree = parse_run_parameters(run_parameters_file)
        create_novaseq_basemask(run_params_tree)
    else:
        run_parameters_file = "runParameters.xml"
        run_params_tree = parse_run_parameters(run_parameters_file)
        create_basemask(run_params_tree, sheet)
