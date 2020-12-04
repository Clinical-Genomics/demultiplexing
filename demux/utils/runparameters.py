""" Parsing of Novaseq run parameters """
import os
from pathlib import Path
import xml.etree.cElementTree as et


class NovaseqRunParameters:
    """ Finds and parses the RunParameters.xml file for a NovaSeq flowcell """

    RUNS_DIR = "/home/hiseq.clinical/novaseq/runs/"
    RUNPARAMETERS_FILE = "RunParameters.xml"

    def __init__(self, flowcell):
        self.flowcell = flowcell
        self.file = self.find_runparameters_file()

    def find_runparameters_file(self):
        """ Find the runparameters file of a based on the flowcell name """

        runparameters_file = None
        for directory in os.scandir(self.RUNS_DIR):
            if self.flowcell in directory.path:
                runparameters_file = os.path.join(directory.path, self.RUNPARAMETERS_FILE)
        if not runparameters_file:
            raise Exception(f"Run parameters for flowcell {self.flowcell} not found!")

        return runparameters_file

    def parse_runparameters(self):
        """ Parse the runparameters file """
        return et.parse(Path(self.file))

    @property
    def control_software_version(self):
        """ Returns the version of the NovaSeq Control Software used """
        return self.parse_runparameters().findtext("ApplicationVersion")

    @property
    def index_reads(self):
        """ Returns the number of index reads """
        return int(self.parse_runparameters().findtext("IndexRead1NumberOfCycles"))

    @property
    def reagent_kit_version(self):
        """ Returns the version of the reagent kit used """
        return self.parse_runparameters().findtext("RfidsInfo/SbsConsumableVersion")
