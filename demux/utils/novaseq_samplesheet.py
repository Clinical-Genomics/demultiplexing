""" Create a samplesheet for Novaseq flowcells """

import csv

from .runparameters import NovaseqRunParameters
from .samplesheet import Samplesheet


DUMMY_INDEXES = "/home/hiseq.clinical/SCRIPTS/git/demultiplexing/files/20181012_Indices.csv"


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

    def __init__(self, flowcell, indexlength, pad, raw_samplesheet):
        self.flowcell = flowcell
        self.indexlength = indexlength
        self.pad = pad
        self.raw_samplesheet = raw_samplesheet
        self.runparameters = NovaseqRunParameters(self.flowcell)

    @property
    def header(self):
        """ Create the sample sheet header """
        return list(Samplesheet.header_map.values())

    @staticmethod
    def get_project(project):
        """ Only keeps the first part of the project name"""
        return project.split(" ")[0]

    @staticmethod
    def reverse_complement(dna):
        """ Generates the reverse complement """
        complement = {"A": "T", "C": "G", "G": "C", "T": "A"}
        return "".join([complement[base] for base in dna[::-1]])

    def add_dummy_indexes(self):
        """ Add all dummy indexes to raw sample sheet """
        with open(f"{DUMMY_INDEXES}") as csv_file:
            dummy_samples_csv = csv.reader(csv_file, delimiter=",")
            dummy_samples = [row for row in dummy_samples_csv]
            added_dummy_samples = []
            lanes = {sample["lane"] for sample in self.raw_samplesheet}

            for lane in lanes:
                sample_indexes = [
                    sample["index"] for sample in self.raw_samplesheet if sample["lane"] == lane
                ]
                for name, dummy_index in dummy_samples:
                    if not (
                        any(sample_index.startswith(dummy_index) for sample_index in sample_indexes)
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
                            "sample_id": name.replace(" ", "-").replace("(", "-").replace(")", "-"),
                            "sample_name": "indexcheck",
                            "sample_ref": "hg19",
                        }

                        added_dummy_samples.append(add_dummy_sample)

            self.raw_samplesheet.extend(added_dummy_samples)

            return self

    def remove_unwanted_indexes(self):
        """ Filter out indexes of unwanted length and single indexes """

        if self.indexlength:
            if self.pad and int(self.indexlength) in (16, 20):
                self.raw_samplesheet = [
                    line
                    for line in self.raw_samplesheet
                    if len(line["index"].replace("-", "")) in (16, int(self.indexlength))
                ]
            else:
                self.raw_samplesheet = [
                    line
                    for line in self.raw_samplesheet
                    if len(line["index"].replace("-", "")) == int(self.indexlength)
                ]
        else:
            self.raw_samplesheet = [line for line in self.raw_samplesheet if "-" in line["index"]]

        return self

    def adapt_indexes(self):
        """Adapts the indexes: pads all indexes so that all indexes have a length equal to the
        number  of index reads, and takes the reverse complement of index 2 in case of the new
        novaseq software control version (1.7) in combination with the new reagent kit
        (version 1.5)"""

        is_reverse_complement = (
            self.runparameters.control_software_version == "1.7.0"
            and self.reagent_kit_version() == 1.5
        )

        for line in self.raw_samplesheet:
            index1, index2 = line["index"].split("-")
            line["index"], line["index2"] = index1, index2
            if self.pad and len(index1) == 8:
                line["index"], line["index2"] = self.pad_and_rc_indexes(
                    index1, index2, is_reverse_complement
                )
            if len(index2) == 10:
                line["index2"] = (
                    self.reverse_complement(index2) if is_reverse_complement else index2
                )

    def pad_and_rc_indexes(self, index1, index2, rev_comp):
        """ Pads and reverse complements indexes """

        if self.runparameters.index_reads == 8:
            index2 = self.reverse_complement(index2) if rev_comp else index2
        if self.runparameters.index_reads == 10:
            index1 = self.reverse_complement("AC" + index1) if rev_comp else index1 + "AT"
            index2 = self.reverse_complement("AC" + index2) if rev_comp else index2 + "AC"

        return index1, index2

    def reagent_kit_version(self):
        """ Derives the reagent kit version from the run parameters """

        parameter_to_version = {"1": 1.0, "3": 1.5}

        return parameter_to_version.get(self.runparameters.reagent_kit_version)

    def construct_samplesheet(self, end="\n", delimiter=","):
        """ Construct the sample sheet """

        demux_samplesheet = [delimiter.join(self.header)]
        self.add_dummy_indexes().remove_unwanted_indexes().adapt_indexes()
        for line in self.raw_samplesheet:
            # fix the project content
            project = self.get_project(line["project"])
            line["project"] = project
            line["sample_name"] = project

            demux_samplesheet.append(
                delimiter.join([str(line[lims_key]) for lims_key in self.LIMS_KEYS])
            )

        return end.join(demux_samplesheet)
