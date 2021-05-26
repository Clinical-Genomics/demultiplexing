""" Create a samplesheet for NovaSeq flowcells """
import csv
import sys
from distutils.version import StrictVersion, LooseVersion
from typing import Any, Dict, List, Union

from cglims.api import ClinicalLims
from demux.constants.constants import COMMA, DASH, SPACE
from demux.constants.samplesheet import (
    NIPT_INDEX_LENGTH,
    PARAMETER_TO_VERSION,
    REV_COMP_CONTROL_SOFTWARE_VERSION,
    REV_COMP_REAGENT_KIT_VERSION,
)
from demux.exc import NoValidReagentKitFound

from .runparameters import NovaseqRunParameters
from .samplesheet import Samplesheet


class CreateNovaseqSamplesheet:
    """Create a raw sample sheet for NovaSeq flowcells"""

    LIMS_KEYS = [
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

    def __init__(
        self,
        dummy_indexes_file: str,
        flowcell: str,
        lims_config: dict,
        pad: bool,
        runs_dir: str,
    ):
        self.dummy_indexes_file = dummy_indexes_file
        self.flowcell = flowcell
        self.lims_api = ClinicalLims(**lims_config)
        self.pad = pad
        self.runparameters = NovaseqRunParameters(self.flowcell, runs_dir)

    @property
    def control_software_version(self) -> StrictVersion:
        """Returns control software version in StrictVersion format"""
        return StrictVersion(self.runparameters.control_software_version)

    @property
    def reagent_kit_version(self) -> LooseVersion:
        """Derives the reagent kit version from the run parameters"""

        reagent_kit_version = self.runparameters.reagent_kit_version
        if reagent_kit_version not in PARAMETER_TO_VERSION.keys():
            raise NoValidReagentKitFound(
                f"Expected reagent kit version {', '.join(PARAMETER_TO_VERSION.keys())}. Found {reagent_kit_version} instead. Exiting",
            )

        return LooseVersion(PARAMETER_TO_VERSION[reagent_kit_version])

    @property
    def header(self) -> list:
        """Create the sample sheet header"""
        return list(Samplesheet.header_map.values())

    def get_dummy_sample_information(
        self, dummy_index: str, lane: int, name: str
    ) -> Dict[Union[str, Any], Union[Union[str, int], Any]]:
        """Constructs and returns a dummy sample in novaseq samplesheet format"""

        return {
            "control": "N",
            "description": "",
            "fcid": self.flowcell,
            "index": dummy_index,
            "index2": "",
            "lane": lane,
            "operator": "script",
            "project": "indexcheck",
            "recipe": "R1",
            "sample_id": name.replace(" ", "-").replace("(", "-").replace(")", "-"),
            "sample_name": "indexcheck",
            "sample_ref": "hg19",
        }

    @staticmethod
    def get_project_name(project: str, delimiter=SPACE) -> str:
        """Only keeps the first part of the project name"""
        return project.split(delimiter)[0]

    @staticmethod
    def get_reverse_complement_dna_seq(dna: str) -> str:
        """Generates the reverse complement of a DNA sequence"""
        complement = {"A": "T", "C": "G", "G": "C", "T": "A"}
        return "".join(complement[base] for base in reversed(dna))

    @staticmethod
    def is_dual_index(index: str, delimiter=DASH) -> bool:
        """Determines if an index in the raw samplesheet is dual index or not"""
        return delimiter in index

    @staticmethod
    def is_dummy_sample_in_samplesheet(dummy_index: str, sample_indexes: list) -> bool:
        """Determines if a dummy sample is already present in the samplesheet"""
        return any(
            sample_index.startswith(dummy_index) for sample_index in sample_indexes
        )

    @staticmethod
    def get_sample_indexes_in_lane(lane: str, raw_samplesheet: List[Dict]) -> list:
        """Returns all sample indexes in a given lane"""
        return [sample["index"] for sample in raw_samplesheet if sample["lane"] == lane]

    def replace_project_with_lims_sample_name(
        self, raw_samplesheet: List[Dict]
    ) -> List[Dict]:
        """Replaces the project in the SampleName column with the LIMS Sample Name"""
        for sample in raw_samplesheet:
            sample["sample_name"] = self.lims_api.sample(sample["sample_id"]).name
        return raw_samplesheet

    def is_reverse_complement(self) -> bool:
        """
        If the run used NovaSeq control software version REV_COMP_CONTROL_SOFTWARE_VERSION or later and reagent
        kit version REV_COMP_REAGENT_KIT_VERSION or later, the second index should be the reverse complement
        """
        return (
            self.control_software_version >= REV_COMP_CONTROL_SOFTWARE_VERSION
            and self.reagent_kit_version >= REV_COMP_REAGENT_KIT_VERSION
        )

    def is_nipt_samplesheet(self) -> bool:
        """Determines if a sample sheet if for NIPT demultiplexing, based on the index length in the run paramaters"""
        return self.runparameters.index_reads == NIPT_INDEX_LENGTH

    def add_dummy_indexes(self, raw_samplesheet: List[Dict]) -> List[Dict]:
        """Add all dummy indexes to raw sample sheet. Dummy indexes are used to check for index
        contamination"""
        with open(f"{self.dummy_indexes_file}") as csv_file:
            dummy_samples_csv = csv.reader(csv_file, delimiter=COMMA)
            dummy_samples = [row for row in dummy_samples_csv]
            new_dummy_samples = []
            lanes = {sample["lane"] for sample in raw_samplesheet}

            for lane in lanes:
                sample_indexes = self.get_sample_indexes_in_lane(lane, raw_samplesheet)
                for sample_name, dummy_index in dummy_samples:
                    if not self.is_dummy_sample_in_samplesheet(
                        dummy_index, sample_indexes
                    ):
                        new_dummy_sample = self.get_dummy_sample_information(
                            dummy_index,
                            lane,
                            sample_name,
                        )
                        new_dummy_samples.append(new_dummy_sample)

            raw_samplesheet.extend(new_dummy_samples)

            return raw_samplesheet

    def remove_unwanted_indexes(self, raw_samplesheet: List[Dict]) -> List[Dict]:
        """Filter out indexes of unwanted length and single indexes"""

        raw_samplesheet = [
            line for line in raw_samplesheet if self.is_dual_index(line["index"])
        ]
        return raw_samplesheet

    def adapt_indexes(self, raw_samplesheet: List[Dict]) -> List[Dict]:
        """Adapts the indexes: pads all indexes so that all indexes have a length equal to the number  of index reads,
        and takes the reverse complement of index 2 in case of the new novaseq software control version
        (1.7) in combination with the new reagent kit (version 1.5)"""

        is_reverse_complement = self.is_reverse_complement()

        for line in raw_samplesheet:
            index1, index2 = line["index"].split("-")
            if self.pad and len(index1) == 8:
                line["index"], line["index2"] = self.pad_and_rc_indexes(
                    index1, index2, is_reverse_complement
                )
            elif len(index2) == 10:
                line["index"] = index1
                line["index2"] = (
                    self.get_reverse_complement_dna_seq(index2)
                    if is_reverse_complement
                    else index2
                )
            else:
                line["index"], line["index2"] = index1, index2

        return raw_samplesheet

    def pad_and_rc_indexes(
        self, index1: str, index2: str, is_reverse_complement: bool
    ) -> tuple:
        """Pads and reverse complements indexes"""

        if self.runparameters.index_reads == 8:
            index2 = (
                self.get_reverse_complement_dna_seq(index2)
                if is_reverse_complement
                else index2
            )
        if self.runparameters.index_reads == 10:
            index1 += "AT"
            index2 = (
                self.get_reverse_complement_dna_seq("AC" + index2)
                if is_reverse_complement
                else index2 + "AC"
            )

        return index1, index2

    def get_raw_samplesheet(self) -> List[Dict]:
        raw_samplesheet = list(self.lims_api.samplesheet(self.flowcell))
        if not raw_samplesheet:
            sys.stderr.write(f"Samplesheet for {self.flowcell} not found in LIMS! ")
            sys.exit()
        return raw_samplesheet

    def construct_samplesheet(self, delimiter=COMMA, end="\n") -> str:
        """Construct the sample sheet"""

        demux_samplesheet = [delimiter.join(self.header)]
        raw_samplesheet = self.get_raw_samplesheet()
        raw_samplesheet = self.replace_project_with_lims_sample_name(raw_samplesheet)
        if not self.is_nipt_samplesheet():
            raw_samplesheet = self.add_dummy_indexes(raw_samplesheet)
        raw_samplesheet = self.remove_unwanted_indexes(raw_samplesheet)
        raw_samplesheet = self.adapt_indexes(raw_samplesheet)
        for line in raw_samplesheet:
            # fix the project content
            project = self.get_project_name(line["project"])
            line["project"] = project

            demux_samplesheet.append(
                delimiter.join([str(line[lims_key]) for lims_key in self.LIMS_KEYS])
            )

        return end.join(demux_samplesheet)
