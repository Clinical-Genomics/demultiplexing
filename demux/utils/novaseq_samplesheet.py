""" Create a samplesheet for Novaseq flowcells """

import csv

from .runparameters import NovaseqRunParameters
from .samplesheet import Samplesheet


class CreateNovaseqSamplesheet:
    """ Create a raw sample sheet for Novaseq flowcells """

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
    NEW_CONTROL_SOFTWARE_VERSION = "1.7.0"
    NEW_REAGENT_KIT_VERSION = 1.5

    def __init__(
        self, flowcell, index_length, pad, raw_samplesheet, dummy_indexes_file, runs_dir
    ):
        self.flowcell = flowcell
        self.index_length = index_length
        self.pad = pad
        self.raw_samplesheet = raw_samplesheet
        self.dummy_indexes_file = dummy_indexes_file
        self.runparameters = NovaseqRunParameters(self.flowcell, runs_dir)

    @property
    def header(self) -> list:
        """ Create the sample sheet header """
        return list(Samplesheet.header_map.values())

    @staticmethod
    def get_project_name(project: str, delimiter=" ") -> str:
        """ Only keeps the first part of the project name """
        return project.split(delimiter)[0]

    @staticmethod
    def reverse_complement(dna: str) -> str:
        """ Generates the reverse complement """
        complement = {"A": "T", "C": "G", "G": "C", "T": "A"}
        return "".join([complement[base] for base in reversed(dna)])

    @staticmethod
    def is_dual_index(index: str, delimiter="-") -> bool:
        """ Determines if an index in the raw samplesheet is dual index or not """
        return delimiter in index

    def is_reverse_complement(self) -> bool:
        """If the run used the new NovaSeq control software version (1.7.0) and the new
        reagent kit version (1.5) the second index should be the reverse complement"""
        return (
            self.runparameters.control_software_version
            == self.NEW_CONTROL_SOFTWARE_VERSION
            and self.reagent_kit_version() == self.NEW_REAGENT_KIT_VERSION
        )

    def add_dummy_indexes(self) -> "CreateNovaseqSamplesheet":
        """ Add all dummy indexes to raw sample sheet """
        with open(f"{self.dummy_indexes_file}") as csv_file:
            dummy_samples_csv = csv.reader(csv_file, delimiter=",")
            dummy_samples = [row for row in dummy_samples_csv]
            added_dummy_samples = []
            lanes = {sample["lane"] for sample in self.raw_samplesheet}

            for lane in lanes:
                sample_indexes = [
                    sample["index"]
                    for sample in self.raw_samplesheet
                    if sample["lane"] == lane
                ]
                for name, dummy_index in dummy_samples:
                    if not (
                        any(
                            sample_index.startswith(dummy_index)
                            for sample_index in sample_indexes
                        )
                    ):
                        add_dummy_sample = {
                            "control": "N",
                            "description": "",
                            "fcid": self.flowcell,
                            "index": dummy_index,
                            "index2": "",
                            "lane": lane,
                            "operator": "script",
                            "project": "indexcheck",
                            "recipe": "R1",
                            "sample_id": name.replace(" ", "-")
                            .replace("(", "-")
                            .replace(")", "-"),
                            "sample_name": "indexcheck",
                            "sample_ref": "hg19",
                        }

                        added_dummy_samples.append(add_dummy_sample)

            self.raw_samplesheet.extend(added_dummy_samples)

            return self

    def remove_unwanted_indexes(self) -> "CreateNovaseqSamplesheet":
        """ Filter out indexes of unwanted length and single indexes """

        self.raw_samplesheet = [
            line for line in self.raw_samplesheet if self.is_dual_index(line["index"])
        ]

        return self

    def adapt_indexes(self) -> "CreateNovaseqSamplesheet":
        """Adapts the indexes: pads all indexes so that all indexes have a length equal to the
        number  of index reads, and takes the reverse complement of index 2 in case of the new
        novaseq software control version (1.7) in combination with the new reagent kit
        (version 1.5)"""

        reverse_complement = self.is_reverse_complement()

        for line in self.raw_samplesheet:
            index1, index2 = line["index"].split("-")
            if self.pad and len(index1) == 8:
                line["index"], line["index2"] = self.pad_and_rc_indexes(
                    index1, index2, reverse_complement
                )
            elif len(index2) == 10:
                line["index2"] = (
                    self.reverse_complement(index2) if reverse_complement else index2
                )
            else:
                line["index"], line["index2"] = index1, index2

        return self

    def pad_and_rc_indexes(
        self, index1: str, index2: str, reverse_complement: bool
    ) -> tuple:
        """ Pads and reverse complements indexes """

        if self.runparameters.index_reads == 8:
            index2 = self.reverse_complement(index2) if reverse_complement else index2
        if self.runparameters.index_reads == 10:
            index1 = index1 + "AT"
            index2 = (
                self.reverse_complement("AC" + index2)
                if reverse_complement
                else index2 + "AC"
            )

        return index1, index2

    def reagent_kit_version(self) -> int:
        """ Derives the reagent kit version from the run parameters """

        parameter_to_version = {"1": 1.0, "3": 1.5}

        return parameter_to_version.get(self.runparameters.reagent_kit_version)

    def construct_samplesheet(self, end="\n", delimiter=",") -> str:
        """ Construct the sample sheet """

        demux_samplesheet = [delimiter.join(self.header)]
        self.add_dummy_indexes().remove_unwanted_indexes().adapt_indexes()
        for line in self.raw_samplesheet:
            # fix the project content
            project = self.get_project_name(line["project"])
            line["project"] = project
            line["sample_name"] = project

            demux_samplesheet.append(
                delimiter.join([str(line[lims_key]) for lims_key in self.LIMS_KEYS])
            )

        return end.join(demux_samplesheet)
