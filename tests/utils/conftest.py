import pytest

from copy import copy

from demux.constants import INDEX_REPORT_HEADER
from demux.utils.indexreport import IndexReport


@pytest.fixture(name="valid_indexreport")
def fixture_valid_indexreport(
    novaseq_valid_indexcheck_report, project_dir
) -> IndexReport:
    """ Fixture of a valid bcl2fastq indexcheck report """
    valid_indexreport = IndexReport(
        out_dir=project_dir,
        index_report_path=novaseq_valid_indexcheck_report,
        flowcell_id="HFKF7DSXY",
        cluster_counts=100000,
        INDEX_REPORT_HEADER=INDEX_REPORT_HEADER,
    )

    return valid_indexreport


@pytest.fixture(name="parsed_indexreport")
def fixture_parsed_indexreport(valid_indexreport) -> IndexReport:
    """ Fixture of a parsed IndexReport class """
    parsed_indexreport = copy(valid_indexreport)
    parsed_indexreport.parse_report()

    return parsed_indexreport


@pytest.fixture(name="validated_indexreport")
def fixture_validated_indexreport(parsed_indexreport) -> IndexReport:
    """ Fixture of a parsed IndexReport class """
    validated_indexreport = copy(parsed_indexreport)
    validated_indexreport.validate()

    return validated_indexreport


@pytest.fixture(name="indexreport_wrong_header_rt1")
def fixture_indexreport_wrong_header_rt1(
    novaseq_indexcheck_wrong_header_rt1, project_dir
):
    indexreport_wrong_header_rt1 = IndexReport(
        out_dir=project_dir,
        index_report_path=novaseq_indexcheck_wrong_header_rt1,
        flowcell_id="HFKF7DSXY",
        cluster_counts=100000,
        INDEX_REPORT_HEADER=INDEX_REPORT_HEADER,
    )
    indexreport_wrong_header_rt1.parse_report()

    return indexreport_wrong_header_rt1


@pytest.fixture(name="indexreport_missing_lanes_rt2")
def fixture_indexreport_missing_lanes_rt2(novaseq_indexcheck_invalid_rt2, project_dir):
    indexreport_missing_lanes_rt2 = IndexReport(
        out_dir=project_dir,
        index_report_path=novaseq_indexcheck_invalid_rt2,
        flowcell_id="HFKF7DSXY",
        cluster_counts=100000,
        INDEX_REPORT_HEADER=INDEX_REPORT_HEADER,
    )
    indexreport_missing_lanes_rt2.parse_report()

    return indexreport_missing_lanes_rt2
