#!/usr/bin/env python
# encoding: utf-8

import sys
from samplesheet import SampleSheet

def main(argv):
    """Makes a SampleSheet NIPT compliant.

    Args:
        argv (path): full path to the SampleSheet.

    """
    ss = SampleSheet(argv[0])
    if 'nuru' in argv:
        ss.massage_normal()
    else:
        ss.massage()
    ss.write()

if __name__ == '__main__':
    main(sys.argv[1:])
