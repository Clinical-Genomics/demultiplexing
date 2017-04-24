#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function
import sys
import re
from copy import deepcopy
from collections import OrderedDict

class SampleSheetValidationException(Exception):
    def __init__(self, section, msg, line_nr):
        self.section = section
        self.msg = msg
        self.line_nr = line_nr

    def __str__(self):
        return repr("Section {}#{}: {}".format(self.section, self.msg, self.line_nr))


class SampleSheetParsexception(Exception):
    pass


class Samplesheet(object):
    """SampleSheet.

    Stores the samplesheet in sections: self.section
    e.g. [Data] section will be stored in self.section['[Data]']

    The [Data] section is the actual samplesheet. It consists of a '[Data]' section marker,
    a column header, and the rows of samplesheet data.

    This will be split on line, with each line turned into a dictionary (column header as keys),
    and stored into self.samplesheet.

    e.g.:
    self.section['[Data]'] = [
        {'Flowcell': 'HHGGFFSS', 'SampleID': 'ADM1123A1', 'Index': 'ACTGACTG'}
    ]

    The original split line with the section marker, will be stored in self.section_markers = ['[Data]','','']

    """

    # known sections
    HEADER = '[Header]'
    DATA   = '[Data]'

    def __init__(self, samplesheet_path):
        self.samplesheet_path = samplesheet_path
        self.original_sheet = [] # all lines of hte samplesheet
        self.section_markers = dict() # [Name]: line; does this section have a named section
        self.parse(samplesheet_path)

    def _get_flowcell(self):
        # get the experiment name
        for line in self.section[self.HEADER]:
            if line[0] == 'Experiment Name':
                return line[1]
        return None

    def _get_project_id(self):
        # get the experiment name
        for line in self.section[self.HEADER]:
            if line[0] == 'Investigator Name':
                return line[1].split('_')[1]
        return None

    def _get_data_header(self):
        return self.section[self.DATA][0]

    def parse(self, samplesheet_path, delim=','):
        """
        Parses a Samplesheet, with their fake csv format.
        Should be instancied with the samplesheet path as an argument.
        Will create a dict for each section. Header: (lines)
        """

        name = '[Data]'
        self.section = OrderedDict()
        with open(samplesheet_path) as csvfile:
            for line in csvfile.readlines():
                line = line.strip()
                line = line.split(delim)
                self.original_sheet.append(line)
                if line[0].startswith('['):
                    name = line[0]
                    self.section_markers[name] = line
                    continue # skip the actual section header

                if name not in self.section:
                    self.section[name] = []

                self.section[name].append(line)

        if self.DATA not in self.section:
            raise SampleSheetParsexception('No data found!')

        header = self._get_data_header()
        self.samplesheet = [ dict(zip(header, line)) for line in self.section[self.DATA][1:] ]

    def lines(self):
        """ Yields all lines of the [Data] section. """
        for line in self.samplesheet:
            yield line

    def raw(self, delim=',', end='\n'):
        """Reconstructs the sample sheet. """
        rs = []
        for line in self.original_sheet:
            rs.append(delim.join(line))
        return end.join(rs)

    def massage(self, delim=',', end='\n'):
        """Abuses the Investigator Name field to store information about the run.

        Reshuffles the [Data] section so that it becomes a valid sample sheet.

        Returns a massaged SampleSheet.
        """
        # get the experiment name
        flowcell_id = self._get_flowcell()

        section_copy = deepcopy(self.section)

        for i, line in enumerate(section_copy[self.HEADER]):
            if line[0] == 'Investigator Name':
                investigator_name = re.split(' |_', line[1])
                if investigator_name[-1] != flowcell_id:
                    investigator_name.append(flowcell_id)
                line[1] = '_'.join(investigator_name)
                section_copy[self.HEADER][i] = line
        
        rs = []
        for section_marker, section in section_copy.items():
            if section_marker in self.section_markers:
                rs.append(delim.join(self.section_markers[section_marker]))
            for line in section:
                rs.append(delim.join(line))
        return end.join(rs)

    def to_demux(self, delim=',', end='\n'):
        """ Replaced the [Data] section with a demuxable [Data] section.

        This is non destructive and will only return a demuxable samplesheet.

        Convert the Data section from
            Lane,Sample_ID,Sample_Name,Sample_Plate,Sample_Well,I7_Index_ID,index,Sample_Project,Description,SampleType
        to
            FCID,Lane,SampleID,SampleRef,Index,Description,Control,Recipe,Operator,SampleProject
        """

        expected_header = ['FCID', 'Lane', 'SampleID', 'SampleRef', 'Index', 'Description', 'Control', 'Recipe', 'Operator', 'SampleProject']

        # get the experiment name
        flowcell_id = self._get_flowcell()
        project_id  = self._get_project_id()

        header = self.section[self.DATA][0] # '0' is the csv header
        data_lines = [] # the new data section. Each line holds a dict with the right header keys
        data_lines.append(expected_header)
        for i, line in enumerate(self.section[self.DATA][1:]):
            data_line = dict(zip(header, line))

            data_line['FCID'] = flowcell_id
            data_line['SampleID'] = data_line['Sample_ID']
            data_line['SampleRef'] = 'hg19'
            data_line['Index'] = data_line['index']
            data_line['Description'] = data_line['SampleType']
            data_line['Control'] = project_id
            data_line['Recipe'] = 'R1'
            data_line['Operator'] = 'NN'
            data_line['SampleProject'] = project_id

            ordered_line = []
            for head in expected_header:
                ordered_line.append(data_line[head])
            data_lines.append(ordered_line)

        rs = []
        for line in data_lines:
            rs.append(delim.join(line))
        return end.join(rs)


    def samples(self, column='SampleID'):
        """ Return all samples in the samplesheet """
        return self.column(column)


    def column(self, column):
        """ Return all values from a column in the samplesheet """
        for line in self.samplesheet:
            yield line[column]

    def lines_per_column(self, column, content):
        """ Return all lines with the same column content
        e.g. return all lines of column='Lane' content='1'  """
        for line in self.samplesheet:
            if line[column] == content:
                yield line

    def is_pooled_lane(self, lane, column='lane'):
        """ Return True if lane contains multiple samples """
        lane_count = 0
        lane = str(lane)
        for line in self.samplesheet:
            if line[column] == lane:
                lane_count += 1

            if lane_count > 1:
                return True

        return False

    def validate(self, seq_type):
        """TODO: Docstring for validate.

        Args:
            seq_type (str): 'wgs', 'wes', 'nipt'

        """

        def _validate_length(section):
            if len(section) > 2:
                for i, line in enumerate(section[1:]):
                    if len(section[0]) != len(line):
                        return ('#fields != #fields in header', i)
            return True

        def _validate_uniq_index(samplesheet):
            lanes = list(set(self.column('Lane')))
            for lane in lanes:
                if self.is_pooled_lane(lane, column='Lane'):
                    sample_of = dict()
                    for line in self.lines_per_column('Lane', lane):
                        if 'index' in line:
                            index = line['index']
                        else:
                            index = line['Index']
                        if index not in sample_of:
                            sample_of[index] = set()
                        sample_of[index].add(line['SampleID'])

                    for index, samples in sample_of.items():
                        if len(samples) > 1:
                            return ('Same index for {} on lane {}'.format(' , '.join(samples), lane), index)

            return True        

        if seq_type != 'nipt':
            rs = _validate_uniq_index(self.samplesheet)
            if type(rs) is tuple:
                raise SampleSheetValidationException(self.DATA, rs[1], rs[0])

        for section_marker, section in self.section.items():
            validation_section = section[:] # only validate the content, not the [Data] header
            rs = _validate_length(validation_section)
            if type(rs) is tuple:
                raise SampleSheetValidationException(section_marker, rs[1], rs[0])


        return True
