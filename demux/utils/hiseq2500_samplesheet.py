""" Create a samplesheet for 2500 flowcells """

from ..constants.constants import DASH, COMMA, LIMS_KEYS
from .samplesheet import Samplesheet


class Create2500Samplesheet:
    """ Create a raw sample sheet for 2500 flowcells """

    def __init__(self, flowcell: str, index_length: int, raw_samplesheet: list):
        self.flowcell = flowcell
        self.index_length = index_length
        self.raw_samplesheet = raw_samplesheet

    @property
    def header(self) -> list:
        """ Create the sample sheet header """
        return list(Samplesheet.header_map.values())

    @staticmethod
    def is_dual_index(index: str, delimiter=DASH) -> bool:
        """ Determines if an index in the raw samplesheet is dual index or not """
        return delimiter in index

    def remove_unwanted_indexes(self, raw_samplesheet: list) -> list:
        """ remove indexes with length unequal to index_length"""
        raw_samplesheet = [
            line
            for line in raw_samplesheet
            if len(line["index"].replace("-", "")) == self.index_length
        ]

        return raw_samplesheet

    def split_dual_indexes(self, raw_samplesheet: list) -> list:
        """ Splits dual indexes"""
        for line in raw_samplesheet:
            if self.is_dual_index(line["index"]):
                index1, index2 = line["index"].split("-")
                line["index"], line["index2"] = index1, index2
        return raw_samplesheet

    def construct_samplesheet(self, end="\n", delimiter=COMMA) -> str:
        """ Construct the sample sheet """
        demux_samplesheet = [delimiter.join(self.header)]
        raw_samplesheet = self.raw_samplesheet
        raw_samplesheet = self.remove_unwanted_indexes(raw_samplesheet)
        raw_samplesheet = self.split_dual_indexes(raw_samplesheet)
        for line in raw_samplesheet:
            line["sample_name"] = line["project"]
            demux_samplesheet.append(
                delimiter.join([str(line[lims_key]) for lims_key in LIMS_KEYS])
            )

        return end.join(demux_samplesheet)
