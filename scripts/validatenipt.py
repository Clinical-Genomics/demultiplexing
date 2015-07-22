#!/usr/bin/env python
# encoding: utf-8

import sys
from samplesheet import SampleSheet

def main(argv):
    """Validates a SampleSheet.
    Will sys.exit when not valid.

    Args:
        argv (path): full path to the SampleSheet.

    """
    ss = SampleSheet(argv[0])
    ss.validate()

if __name__ == '__main__':
    main(sys.argv[1:])
