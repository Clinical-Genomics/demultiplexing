import pytest

from bs4.element import Tag
from copy import copy
from pathlib import Path

from demux.constants import report_tables_index, reference_report_header
from demux.utils.indexreport import IndexReport


@pytest.fixture(name="valid_indexreport")
def fixture_valid_indexreport(
    novaseq_valid_indexcheck_report: Path, project_dir: Path, s4_run_parameters: Path
) -> IndexReport:
    """Fixture of a valid bcl2fastq indexcheck report"""
    valid_indexreport = IndexReport(
        out_dir=project_dir,
        index_report_path=novaseq_valid_indexcheck_report,
        cluster_counts=100000,
        report_tables_index=report_tables_index,
        run_parameters_path=s4_run_parameters
    )

    return valid_indexreport


@pytest.fixture(name="parsed_indexreport")
def fixture_parsed_indexreport(valid_indexreport: IndexReport) -> IndexReport:
    """Fixture of a parsed IndexReport class"""
    parsed_indexreport = copy(valid_indexreport)

    return parsed_indexreport


@pytest.fixture(name="validated_indexreport")
def fixture_validated_indexreport(parsed_indexreport: IndexReport) -> IndexReport:
    """Fixture of a parsed IndexReport object"""
    validated_indexreport = copy(parsed_indexreport)
    validated_indexreport.validate(reference_report_header=reference_report_header)

    return validated_indexreport


@pytest.fixture(name="indexreport_wrong_header_rt1")
def fixture_indexreport_wrong_header_rt1(
    novaseq_indexcheck_wrong_header_rt1: Path, project_dir: Path, s4_run_parameters: Path
) -> IndexReport:
    """Fixture of a corrupt IndexReport object, faulty headers in sample cluster count table"""
    indexreport_wrong_header_rt1 = IndexReport(
        out_dir=project_dir,
        index_report_path=novaseq_indexcheck_wrong_header_rt1,
        cluster_counts=100000,
        report_tables_index=report_tables_index,
        run_parameters_path=s4_run_parameters
    )

    return indexreport_wrong_header_rt1


@pytest.fixture(name="indexreport_missing_lanes_rt2")
def fixture_indexreport_missing_lanes_rt2(
    novaseq_indexcheck_invalid_rt2: Path, project_dir: Path, s4_run_parameters: Path
) -> IndexReport:
    """Fixture of a corrupt IndexReport object, missing lanes in top unknown"""
    indexreport_missing_lanes_rt2 = IndexReport(
        out_dir=project_dir,
        index_report_path=novaseq_indexcheck_invalid_rt2,
        cluster_counts=100000,
        report_tables_index=report_tables_index,
        run_parameters_path=s4_run_parameters
    )

    return indexreport_missing_lanes_rt2


@pytest.fixture(name="indexreport_sample_table_row")
def fixture_indexreport_sample_table_row(valid_indexreport: IndexReport) -> Tag:
    """Return the first row in the cluster count sample table"""
    return valid_indexreport.report_tables[
        report_tables_index["cluster_count_table"]
    ].find_all("tr")[1:][0]


@pytest.fixture(name="indexreport_sample_table_header")
def fixture_indexreport_sample_table_header(validated_indexreport: IndexReport) -> Tag:
    """Return the header for cluster count sample table from a valid index report"""
    return validated_indexreport.report_tables[
        report_tables_index["cluster_count_table"]
    ].tr.find_all("th")

