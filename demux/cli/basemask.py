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
    type=click.Choice(["miseq", "nipt", "nova", "wes", "wgs"]),
    help="sequencing type",
)
def create(rundir, lane, application):
    """Create a basemask based on SampleSheet.csv and runParameters"""

    # runParameters.xml
    def parse_run_parameters(run_parameters_file):
        """ parse the run parameters file """
        return xml_etree.parse(Path(rundir).joinpath(run_parameters_file))

    def create_basemask(sheet):
        """ create the bcl2fastq basemask """
        run_parameters_file = "runParameters.xml"
        run_params_tree = parse_run_parameters(run_parameters_file)
        read1_len = int(run_params_tree.findtext("Setup/IndexRead1"))
        read2_len = int(run_params_tree.findtext("Setup/IndexRead2"))

        lines = [line for line in sheet.lines_per_column("lane", lane)]

        # get the index lengths
        index1 = lines[0]["index"]
        index2 = lines[0]["index2"] if "index2" in lines[0] else EMPTY_STRING

        # index1 basemask
        index1_n = "n" * (read1_len - len(index1))
        basemask_index1 = "I" + str(len(index1)) + index1_n

        # index2 basemask
        if read2_len == 0:
            click.echo(f"Y151,{basemask_index1},Y151")
        else:
            index2_n = "n" * (read2_len - len(index2))
            if len(index2) > 0:
                basemask_index2 = "I" + str(len(index2)) + index2_n
            else:
                basemask_index2 = index2_n
            click.echo(f"Y151,{basemask_index1},{basemask_index2},Y151")

    def create_novaseq_basemask():
        """ create the bcl2fastq basemask for novaseq flowcells"""

        run_parameters_file = "RunParameters.xml"
        run_params_tree = parse_run_parameters(run_parameters_file)

        indexread1 = int(run_params_tree.findtext("IndexRead1NumberOfCycles"))
        indexread2 = int(run_params_tree.findtext("IndexRead2NumberOfCycles"))
        read1 = int(run_params_tree.findtext("Read1NumberOfCycles"))
        read2 = int(run_params_tree.findtext("Read2NumberOfCycles"))

        novaseq_basemask = f"Y{read1},I{indexread1},I{indexread2},Y{read2}"

        click.echo(f"{novaseq_basemask}")

    def get_application_sheet(application):
        """ parse the samplesheet in the runs directory, based on the type of application """
        sheet = None
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
        """ determine the basemask """
        if application == "nova":
            create_novaseq_basemask()
        else:
            create_basemask(get_application_sheet(application))

    create_application_basemask(application)
