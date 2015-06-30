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
        """TODO: to be defined1. """
        self.parse(path)

    def parse(self, path):
        """Parses Xten Samplesheets, with their fake csv format.
        Should be instancied with the samplesheet path as an argument.
        .header : a dict containing the info located under the [Header] section
        .settings : a dict containing the data from the [Settings] section
        .reads : a list of the values in the [Reads] section
        .data : a list of the values under the [Data] section. These values are stored in a dict format
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
        """TODO: Docstring for write.

        """
        for line in chain(*self.section.values()):
            print(','.join(line))

    def massage(self):
        """TODO: Docstring for massage.
        Returns: TODO

        """
        # get the experiment name
        flowcell_id = ''
        for line in self.section[self.HEADER]:
            if line[0] == 'Experiment Name':
                flowcell_id = line[1]
                break

        for i, line in enumerate(self.section[self.HEADER]):
            if line[0] == 'Investigator Name':
                investigator_name = re.split(' |_', line[1])
                if investigator_name[-1] != flowcell_id:
                    investigator_name.append(flowcell_id)
                line[1] = '_'.join(investigator_name)
                self.section[self.HEADER][i] = line

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
    ss.massage()
    ss.write()

if __name__ == '__main__':
    main(sys.argv[1:])
