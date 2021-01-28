import pytest

from copy import copy

from demux.constants import report_tables_index, reference_report_header
from demux.utils.indexreport import IndexReport


@pytest.fixture(name="valid_indexreport")
def fixture_valid_indexreport(
    novaseq_valid_indexcheck_report, project_dir
) -> IndexReport:
    """Fixture of a valid bcl2fastq indexcheck report"""
    valid_indexreport = IndexReport(
        out_dir=project_dir,
        index_report_path=novaseq_valid_indexcheck_report,
        flowcell_id="HFKF7DSXY",
        cluster_counts=100000,
        report_tables_index=report_tables_index,
    )

    return valid_indexreport


@pytest.fixture(name="parsed_indexreport")
def fixture_parsed_indexreport(valid_indexreport) -> IndexReport:
    """Fixture of a parsed IndexReport class"""
    parsed_indexreport = copy(valid_indexreport)

    return parsed_indexreport


@pytest.fixture(name="validated_indexreport")
def fixture_validated_indexreport(parsed_indexreport) -> IndexReport:
    """Fixture of a parsed IndexReport object"""
    validated_indexreport = copy(parsed_indexreport)
    validated_indexreport.validate(reference_report_header=reference_report_header)

    return validated_indexreport


@pytest.fixture(name="indexreport_wrong_header_rt1")
def fixture_indexreport_wrong_header_rt1(
    novaseq_indexcheck_wrong_header_rt1, project_dir
):
    """Fixture of a corrupt IndexReport object, faulty headers in sample cluster count table"""
    indexreport_wrong_header_rt1 = IndexReport(
        out_dir=project_dir,
        index_report_path=novaseq_indexcheck_wrong_header_rt1,
        flowcell_id="HFKF7DSXY",
        cluster_counts=100000,
        report_tables_index=report_tables_index,
    )

    return indexreport_wrong_header_rt1


@pytest.fixture(name="indexreport_missing_lanes_rt2")
def fixture_indexreport_missing_lanes_rt2(novaseq_indexcheck_invalid_rt2, project_dir):
    """Fixture of a corrupt IndexReport object, missing lanes in top unknown"""
    indexreport_missing_lanes_rt2 = IndexReport(
        out_dir=project_dir,
        index_report_path=novaseq_indexcheck_invalid_rt2,
        flowcell_id="HFKF7DSXY",
        cluster_counts=100000,
        report_tables_index=report_tables_index,
    )

    return indexreport_missing_lanes_rt2
