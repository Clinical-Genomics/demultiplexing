import pytest
import logging
import bs4

from pathlib import Path

from demux.constants import REFERENCE_REPORT_HEADER, REPORT_TABLES_INDEX
from demux.exc import IndexReportError
from demux.utils.indexreport import (
    IndexReport,
    validate_index_report_header,
    validate_report_tables,
    validate_top_unknown_barcodes_table,
)


LOG = logging.getLogger(__name__)


def test_parse_indexreport(
    caplog,
    novaseq_valid_indexcheck_report: Path,
    project_dir: Path,
    s4_run_parameters: Path,
):
    """Test the function to parse a bcl2fastq indexcheck html report"""

    # GIVEN a valid input bcl2fastq report
    caplog.set_level(logging.INFO)
    # WHEN parsing said report
    IndexReport(
        out_dir=project_dir,
        index_report_path=novaseq_valid_indexcheck_report,
        cluster_counts=100000,
        report_tables_index=REPORT_TABLES_INDEX,
        run_parameters_path=s4_run_parameters,
    )
    # THEN we should pass parsing and see
    assert "Parsing complete!" in caplog.text


def test_validate_top_unknown_barcodes_table(
    empty_top_unknown_barcodes_table: bs4.BeautifulSoup,
):
    """Test the validation of a empty top unknown barcodes table"""

    # GIVEN a empty top unknown barcodes table

    # WHEN validating said table
    valid, message = validate_top_unknown_barcodes_table(
        top_unknown_barcodes_table=empty_top_unknown_barcodes_table,
        flowcell_version="S4",
    )

    # THEN we should see that it is not valid and the following message
    assert not valid
    assert (
        message
        == "Top unknown barcode table is not matching the reference, please check the report"
    )


def test_validate_report_tables(missing_report_tables: bs4.ResultSet):

    # GIVEN missing report tables set

    # WHEN validating said set
    valid, message = validate_report_tables(report_tables=missing_report_tables)

    # THEN we should see that it is not valid and the following message
    assert not valid
    assert (
        message
        == "The number of Report Tables are not matching the reference, please check the report"
    )


def test_validate_index_report_header(modified_report_sample_table_header: dict):

    # GIVEN a modified report sample table header, missing a column

    # WHEN validating said header
    valid, message = validate_index_report_header(
        reference_header=REFERENCE_REPORT_HEADER,
        sample_table_header=modified_report_sample_table_header,
    )

    # THEN we should see that it is not valid and the following message
    assert not valid
    assert message == (
        f"The header in the cluster count sample table is not matching the\n"
        f"control headers. Check if they need correction"
    )


def test_validate_valid_indexreport(caplog, parsed_indexreport: IndexReport):
    """Test validation on valid indexcheck report"""

    # GIVEN a valid parsed bcl2fastq
    caplog.set_level(logging.INFO)
    # WHEN validating said "valid" report
    parsed_indexreport.validate(reference_report_header=REFERENCE_REPORT_HEADER)
    # THEN validations should be passed
    assert "Validation passed" in caplog.text


def test_write_report(caplog, validated_indexreport: IndexReport):
    """Test writing function of a summary"""

    # GIVEN a validated bcl2fastq report
    caplog.set_level(logging.INFO)
    # WHEN we compile the summary report
    validated_indexreport.write_summary(report_tables_index=REPORT_TABLES_INDEX)
    # THEN we should create a report and see the message
    assert "Wrote indexcheck report summary to" in caplog.text


def test_validate_wrong_header_rt1(caplog, indexreport_wrong_header_rt1):
    """Test validation of faulty headers in Report Table 1"""

    # GIVEN a corrupt bcl2fastq indexcheck report with faulty headers
    caplog.set_level(logging.ERROR)
    # WHEN the corrupt bcl2fastq indexcheck report is validated
    with pytest.raises(IndexReportError) as e:
        indexreport_wrong_header_rt1.validate(
            reference_report_header=REFERENCE_REPORT_HEADER
        )
    # THEN an exception is raised and a message is reported
    assert (
        f"The header in the cluster count sample table is not matching the\n"
        f"control headers. Check if they need correction"
    ) in caplog.text


def test_validate_missing_lanes_rt2(caplog, indexreport_missing_lanes_rt2):
    """Test the validation of missing lanes and thus structure in Report table 2"""

    # GIVEN a corrupt bcl2fastq indexcheck report with missing lanes
    caplog.set_level(logging.ERROR)
    # WHEN the corrupt bcl2fastq indexcheck report is validated
    with pytest.raises(IndexReportError) as e:
        indexreport_missing_lanes_rt2.validate(
            reference_report_header=REFERENCE_REPORT_HEADER
        )
    # THEN an report error should be raised and the following message prompted
    assert (
        f"Top unknown barcode table is not matching the reference, please check the report"
    ) in caplog.text
