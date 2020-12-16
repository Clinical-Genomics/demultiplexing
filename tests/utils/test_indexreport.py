import pytest
import logging
import os

from pathlib import Path

from demux.constants import INDEX_REPORT_HEADER
from demux.utils.indexreport import IndexReport

log = logging.getLogger(__name__)

# TO DO:
# tempdir in conftest


def test_parse_indexreport(novaseq_valid_indexcheck_report: Path):
    """ Test the function to parse a bcl2fastq indextcheck html report"""
    with open(novaseq_valid_indexcheck_report, 'r') as fh:
        index_report = IndexReport(
            out_dir=Path('.'),
            index_report_path=fh,
            flowcell_id='HX1234DSXY',
            INDEX_REPORT_HEADER=INDEX_REPORT_HEADER,
            cluster_counts=100000,
            log=log
        )


        index_report.parse_report()
        print(index_report.log.info)


# test write function
# test validation function