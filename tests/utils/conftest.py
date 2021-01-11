import pytest

from copy import deepcopy

from demux.constants import INDEX_REPORT_HEADER
from demux.utils.indexreport import IndexReport


@pytest.fixture(name="valid_indexreport")
def fixture_index_check_report(novaseq_valid_indexcheck_report, project_dir) -> IndexReport:
    """ Fixture of a valid bcl2fastq indexcheck report """
    index_check_report = IndexReport(
        out_dir=project_dir,
        index_report_path=novaseq_valid_indexcheck_report,
        flowcell_id="HFKF7DSXY",
        cluster_counts=100000,
        INDEX_REPORT_HEADER=INDEX_REPORT_HEADER
    )

    return index_check_report


@pytest.fixture(name="parsed_valid_indexreport")
def fixture_parsed_valid_indexreport(valid_indexreport) -> IndexReport:
    """ Fixture of a parsed bcl2fastq indexcheck report """
    parsed_valid_indexreport = deepcopy(valid_indexreport)
    parsed_valid_indexreport.parse_report()

    return parsed_valid_indexreport


@pytest.fixture(name="validated_indexreport")
def fixture_parsed_valid_indexreport(parsed_valid_indexreport) -> IndexReport:
    """ Fixture of a validated bcl2fastq indexcheck report """
    parsed_valid_indexreport = deepcopy(parsed_valid_indexreport)
    parsed_valid_indexreport.validate()

    return parsed_valid_indexreport


@pytest.fixture(name="indexreport_wrong_header_rt1")
def fixture_indexreport_wrong_header_rt1(novaseq_indexcheck_wrong_header_rt1, project_dir):
    indexreport_wrong_header_rt1 = IndexReport(
        out_dir=project_dir,
        index_report_path=novaseq_indexcheck_wrong_header_rt1,
        flowcell_id="HFKF7DSXY",
        cluster_counts=100000,
        INDEX_REPORT_HEADER=INDEX_REPORT_HEADER
    )
    indexreport_wrong_header_rt1.parse_report()

    return indexreport_wrong_header_rt1
