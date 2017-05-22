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

    [Data],,
    Flowcell,SampleID,Index
    HHGGFFSS,ADM1123A1,ACTGACTG

    self.section['[Data]'] = [
        {'FCID': 'HHGGFFSS', 'SampleID': 'ADM1123A1', 'Index': 'ACTGACTG'}
    ]

    The original split line with the section marker, will be stored in self.section_markers['[Data]'] = ['[Data]','','']

    """

    # known sections
    HEADER = '[Header]'
    DATA   = '[Data]'

    # for the [Data] section: provide a universal header line.
    # The mapping is like this: universal: expected, e.g. for NIPT we have expected Sample_ID,
    # which is mapped to the more universal 'sample_id': 'sample_id': 'Sample_ID'
    # Universal keys follow the python variable naming rules:
    # lowercase with words separated by underscores as necessary to improve readability.
    # One can make one header map for each samplesheet type.
    header_map = {
            'fcid': 'FCID', 'lane': 'Lane', 'sample_id': 'SampleID', 'sample_ref': 'SampleRef',
            'index': 'index', 'sample_name': 'SampleName', 'control': 'Control', 'recipe': 'Recipe',
            'operator': 'Operator', 'project': 'Project'
    }

    def _get_flowcell(self):
        for line in self.section[self.DATA]:
            if 'Flowcell' in line:
                return line['Flowcell']
        return None

    def __init__(self, samplesheet_path):
        self.samplesheet_path = samplesheet_path
        self.original_sheet = [] # all lines of hte samplesheet
        self.section_markers = dict() # [Name]: line; does this section have a named section
        self.parse(samplesheet_path)

    def _get_data_header(self):
        return self.section[self.DATA][0]

    def _get_header_key(self, key):
        if key not in self.header_map:
            raise KeyError("'{}' not in header_map!".format(key))
        return self.header_map[key]

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
        header_map_r = dict((v,k) for k,v in self.header_map.iteritems())
        for line_r in self.samplesheet:
            line = {}
            for key_r in line_r.keys():
                if key_r in header_map_r:
                    key = header_map_r[key_r]
                    line[key] = line_r[key_r]
            yield line

    def lines_r(self):
        """ Yields all lines of the [Data] section based on the original header """
        for line in self.samplesheet:
            yield line

    def raw(self, delim=',', end='\n'):
        """Reconstructs the sample sheet. """
        rs = []
        for line in self.original_sheet:
            rs.append(delim.join(line))
        return end.join(rs)

    def samples(self, column='sample_id'):
        """ Return all samples in the samplesheet """
        return self.column(column)

    def samples_r(self, column='SampleID'):
        """ Return all samples in the samplesheet based on the original header"""
        return self.column_r(column)

    def column(self, column):
        """ Return all values from a column in the samplesheet """
        for line in self.samplesheet:
            yield line[ self._get_header_key(column) ]

    def column_r(self, column):
        """ Return all values from a column in the samplesheet based on the original header"""
        for line in self.samplesheet:
            yield line[column]

    def cell(self, line, column):
        """ return the contents of a column in a line """

        return line[ self._get_header_key(column) ]

    def lines_per_column(self, column, content):
        """ Return all lines with the same column content
        e.g. return all lines of column='Lane' content='1'  """
        column = self._get_header_key(column)
        for line in self.samplesheet:
            if line[column] == content:
                yield line

    def lines_per_column_r(self, column, content):
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
            if line[ self._get_header_key(column) ] == lane:
                lane_count += 1

            if lane_count > 1:
                return True

        return False

    def is_pooled_lane_r(self, lane, column='lane'):
        """ Return True if lane contains multiple samples based on the orignal header """
        lane_count = 0
        lane = str(lane)
        for line in self.samplesheet:
            if line[column] == lane:
                lane_count += 1

            if lane_count > 1:
                return True

        return False

    def validate(self):
        """ General validation of a samplesheet """

        def _validate_length(section):
            if len(section) > 2:
                for i, line in enumerate(section[1:]):
                    if len(section[0]) != len(line):
                        return ('#fields != #fields in header', i)
            return True

        def _validate_uniq_index(samplesheet):
            lanes = list(set(self.column('lane')))
            for lane in lanes:
                if self.is_pooled_lane(lane, column='lane'):
                    sample_of = dict()
                    for line in self.lines_per_column('lane', lane):
                        index = self.cell(line, 'index')
                        if index not in sample_of:
                            sample_of[index] = set()
                        sample_of[index].add(self.cell(line, 'sample_id'))

                    for index, samples in sample_of.items():
                        if len(samples) > 1:
                            return ('Same index for {} on lane {}'.format(' , '.join(samples), lane), index)

            return True

        rs = _validate_uniq_index(self.samplesheet)
        if type(rs) is tuple:
            raise SampleSheetValidationException(self.DATA, rs[1], rs[0])

        for section_marker, section in self.section.items():
            validation_section = section[:] # only validate the content, not the [Data] header
            rs = _validate_length(validation_section)
            if type(rs) is tuple:
                raise SampleSheetValidationException(section_marker, rs[1], rs[0])


        return True


class HiSeq2500Samplesheet(Samplesheet):

    header_map = {
            'fcid': 'FCID', 'lane': 'Lane', 'sample_id': 'SampleID', 'sample_ref': 'SampleRef',
            'index': 'Index', 'sample_name': 'SampleName', 'control': 'Control', 'recipe': 'Recipe',
            'operator': 'Operator', 'description': 'Description', 'project': 'SampleProject'
    }


class NIPTSamplesheet(Samplesheet):

    header_map = { 
            'lane': 'Lane', 'sample_id': 'Sample_ID', 'sample_name': 'Sample_Name',
            'sample_plate': 'Sample_Plate', 'sample_well': 'Sample_Well',
            'i7_index_id': 'I7_Index_ID', 'index': 'index', 'sample_project': 'Sample_Project',
            'description': 'Description', 'sample_type': 'SampleType', 'library_nm': 'Library_nM'
    }

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

