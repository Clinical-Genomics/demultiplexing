#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function
import sys
import re
from itertools import chain
from collections import OrderedDict

class SampleSheet(object):
    """Docstring for SampleSheet. """

    HEADER = '[Header]'
    DATA   = '[Data]'

    def __init__(self, path):
        self.parse(path)

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

    def parse(self, path):
        """
        Parses Samplesheets, with their fake csv format.
        Should be instancied with the samplesheet path as an argument.
	Will create a dict for each section. Header: (lines)
        """

        name = 'None'
        self.section = OrderedDict()
        with open(path) as csvfile:
            for line in csvfile.readlines():
                line = line.strip()
                if line.startswith('['):
                    name = line.split(',')[0]
                    self.section[name] = []

                self.section[name].append(line.split(','))

    def write(self):
        """Writes a SampleSheet to disk

        """
        for line in chain(*self.section.values()):
            print(','.join(line))

    def massage(self):
        """Abuses the Investigator Name field to store information about the run.

	Reshuffles the [Data] section so that it becomes a valid sample sheet.
        """
        # get the experiment name
        flowcell_id = self._get_flowcell()

        for i, line in enumerate(self.section[self.HEADER]):
            if line[0] == 'Investigator Name':
                investigator_name = re.split(' |_', line[1])
                if investigator_name[-1] != flowcell_id:
                    investigator_name.append(flowcell_id)
                line[1] = '_'.join(investigator_name)
                self.section[self.HEADER][i] = line

    def massage_normal(self):
        """ Replaced the [Data] section with a demuxable [Data] section.

        BE AWARE THIS IS DESTRUCTIVE!

	Convert the Data section from
            Lane,Sample_ID,Sample_Name,Sample_Plate,Sample_Well,I7_Index_ID,index,Sample_Project,Description,SampleType
        to
	    FCID,Lane,SampleID,SampleRef,Index,Description,Control,Recipe,Operator,SampleProject
	"""

	expected_header = ['FCID', 'Lane', 'SampleID', 'SampleRef', 'Index', 'Description', 'Control', 'Recipe', 'Operator', 'SampleProject']

        # get the experiment name
        flowcell_id = self._get_flowcell()
        project_id  = self._get_project_id()

        header = self.section[self.DATA][1] # '0' is the section header, '1' is the csv header
        data_lines = [] # the new data section. Each line holds a dict with the right header keys
        #data_lines.append(self.section[self.DATA][0])
        data_lines.append(expected_header)
        for i, line in enumerate(self.section[self.DATA][2:]):
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

        self.section[self.DATA] = data_lines
        for key in self.section.keys():
            if key == self.DATA: continue
            self.section.pop(key, None)

    def validate(self):
        """TODO: Docstring for validate.

        Returns: TODO

        """

        def _validate_length(section):
            """TODO: Docstring for function.

            Args:
                arg1 (TODO): TODO

            Returns: TODO

            """

            if len(section) > 2:
                for i, line in enumerate(section[1:]):
                    if len(section[0]) != len(line):
                        return ('#fields != #fields in header', i)
            return True

        for section_name, section in self.section.items():
            rs = _validate_length(section)
            if type(rs) is tuple:
                sys.exit('Section {}#{}: {}'.format(section_name, rs[1], rs[0]))

def main(argv):
    ss = SampleSheet(argv[0])
    ss.validate()
    if 1 in argv:
        ss.massage_normal()
    else:
        ss.massage()
    ss.write()

if __name__ == '__main__':
    main(sys.argv[1:])
