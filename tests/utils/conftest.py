from copy import copy
from pathlib import Path

import bs4
import pytest

from demux.constants import REFERENCE_REPORT_HEADER, REPORT_TABLES_INDEX
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
        report_tables_index=REPORT_TABLES_INDEX,
        run_parameters_path=s4_run_parameters,
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
    validated_indexreport.validate(reference_report_header=REFERENCE_REPORT_HEADER)

    return validated_indexreport


@pytest.fixture(name="indexreport_wrong_header_rt1")
def fixture_indexreport_wrong_header_rt1(
    novaseq_indexcheck_wrong_header_rt1: Path,
    project_dir: Path,
    s4_run_parameters: Path,
) -> IndexReport:
    """Fixture of a corrupt IndexReport object, faulty headers in sample cluster count table"""
    indexreport_wrong_header_rt1 = IndexReport(
        out_dir=project_dir,
        index_report_path=novaseq_indexcheck_wrong_header_rt1,
        cluster_counts=100000,
        report_tables_index=REPORT_TABLES_INDEX,
        run_parameters_path=s4_run_parameters,
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
        report_tables_index=REPORT_TABLES_INDEX,
        run_parameters_path=s4_run_parameters,
    )

    return indexreport_missing_lanes_rt2


@pytest.fixture(name="indexreport_sample_table_row")
def fixture_indexreport_sample_table_row(
    valid_indexreport: IndexReport,
) -> bs4.element.Tag:
    """Return the first row in the cluster count sample table"""
    return valid_indexreport.report_tables[
        REPORT_TABLES_INDEX["cluster_count_table"]
    ].find_all("tr")[1:][0]


@pytest.fixture(name="indexreport_sample_table_header")
def fixture_indexreport_sample_table_header(
    validated_indexreport: IndexReport,
) -> bs4.element.Tag:
    """Return the header for cluster count sample table from a valid index report"""
    return validated_indexreport.report_tables[
        REPORT_TABLES_INDEX["cluster_count_table"]
    ].tr.find_all("th")


@pytest.fixture(name="empty_top_unknown_barcodes_table")
def fixture_empty_top_unknown_barcodes_table() -> bs4:
    """Return an empty top unknown barcodes table"""
    empty_top_unknown_barcodes_table = bs4.BeautifulSoup(
        "<html><body><tr></tr></body></html>", "html.parser"
    )
    return empty_top_unknown_barcodes_table


@pytest.fixture(name="missing_report_tables")
def fixture_missing_report_tables(valid_indexreport: IndexReport) -> bs4.ResultSet:
    """Return, from a report with a missing report tables, report tables of a indexreport"""
    missing_report_tables = valid_indexreport.report_tables[:-1]
    return missing_report_tables


@pytest.fixture(name="modified_report_sample_table_header")
def fixture_modified_report_sample_table_header(valid_indexreport: IndexReport) -> dict:
    """Return a sample table header with a missing column"""
    modified_report = copy(valid_indexreport)
    modified_report.sample_table_header.pop("Lane")
    return modified_report.sample_table_header


@pytest.fixture(name="hiseq2500_samplesheet_invalid_duplicate_index")
def fixture_invalid_2500_samplesheet_duplicate_index(hiseq2500_dir):
    """fixture for an invalid 2500 sample sheet with a duplicate index"""
    return hiseq2500_dir / "2500-single-index-samplesheet-invalid-duplicate-index.csv"


@pytest.fixture(name="hiseq2500_samplesheet_invalid_length")
def fixture_invalid_2500_samplesheet_length(hiseq2500_dir):
    """fixture for an invalid 2500 sample sheet with a line that is longer than the header"""
    return hiseq2500_dir / "2500-single-index-samplesheet-invalid-length.csv"


@pytest.fixture(name="hiseq2500_samplesheet_invalid_sample_name")
def fixture_invalid_2500_samplesheet_sample_name(hiseq2500_dir):
    """fixture for an invalid 2500 sample sheet with a sample name with a space in it"""
    return hiseq2500_dir / "2500-single-index-samplesheet-invalid-sample-name.csv"


@pytest.fixture(name="hiseq2500_samplesheet_valid")
def fixture_valid_2500_samplesheet(hiseq2500_dir):
    """fixture for a valid 2500 sample sheet"""
    return hiseq2500_dir / "2500-single-index-samplesheet-valid.csv"
