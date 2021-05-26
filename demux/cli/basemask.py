""" create basemask for demultiplexing based on run parameters """

import logging
import xml.etree.cElementTree as xml_etree
from pathlib import Path

import click

from ..utils import (
    HiSeq2500Samplesheet,
    HiSeqXSamplesheet,
    MiseqSamplesheet,
    NIPTSamplesheet,
)

EMPTY_STRING = ""
LOG = logging.getLogger(__name__)


@click.group()
def basemask():
    """Samplesheet commands"""


@basemask.command()
@click.argument("rundir")
@click.option("-l", "--lane", help="lane number")
@click.option(
    "-a",
    "--application",
    type=click.Choice(["miseq", "nipt", "wes", "wgs"]),
    help="sequencing type",
)
def create(rundir, lane, application):
    """Create a basemask based on SampleSheet.csv and runParameters"""

    # runParameters.xml
    def parse_run_parameters():
        """parse the run parameters file"""
        return xml_etree.parse(Path(rundir).joinpath("runParameters.xml"))

    def create_basemask(sheet):
        """create the bcl2fastq basemask"""
        run_params_tree = parse_run_parameters()
        read1 = int(run_params_tree.findtext("Setup/Read1"))
        read2 = int(run_params_tree.findtext("Setup/Read2"))
        indexread1 = int(run_params_tree.findtext("Setup/IndexRead1"))
        indexread2 = int(run_params_tree.findtext("Setup/IndexRead2"))

        lines = [line for line in sheet.lines_per_column("lane", lane)]

        # get the index lengths
        index1 = lines[0]["index"]
        index2 = lines[0]["index2"] if "index2" in lines[0] else EMPTY_STRING

        # index1 basemask
        index1_n = "n" * (indexread1 - len(index1))
        basemask_index1 = "I" + str(len(index1)) + index1_n

        # index2 basemask
        if indexread2 == 0:
            click.echo(f"Y{read1},{basemask_index1},Y{read2}")
        else:
            index2_n = "n" * (indexread2 - len(index2))
            if len(index2) > 0:
                basemask_index2 = "I" + str(len(index2)) + index2_n
            else:
                basemask_index2 = index2_n
            click.echo(f"Y{read1},{basemask_index1},{basemask_index2},Y{read2}")

    def get_application_sheet(application):
        """parse the samplesheet in the runs directory, based on the type of application"""
        samplesheet = Path(rundir).joinpath("SampleSheet.csv")
        sheet_map = {
            "nipt": NIPTSamplesheet,
            "wes": HiSeq2500Samplesheet,
            "miseq": MiseqSamplesheet,
            "wgs": HiSeqXSamplesheet,
        }
        sheet = sheet_map[application](samplesheet)

        return sheet

    def create_application_basemask(application):
        """determine the basemask"""
        create_basemask(get_application_sheet(application))

    create_application_basemask(application)
