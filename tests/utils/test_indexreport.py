import pytest
import logging

from pathlib import Path

from demux.exc import IndexReportError
from demux.utils.indexreport import IndexReport

LOG = logging.getLogger(__name__)


def test_parse_indexreport(
    novaseq_valid_indexcheck_report: Path, project_dir: Path, caplog
):
    """Test the function to parse a bcl2fastq indexcheck html report"""

    # GIVEN a valid input bcl2fastq report
    caplog.set_level(logging.INFO)
    # WHEN parsing said report
    IndexReport(
        out_dir=project_dir,
        index_report_path=novaseq_valid_indexcheck_report,
        flowcell_id="HFKF7DSXY",
        cluster_counts=100000,
    )
    # THEN we should pass parsing and see
    assert "Parsing complete!" in caplog.text


def test_validate_valid_indexreport(parsed_indexreport: IndexReport, caplog):
    """Test validation on valid indexcheck report"""

    # GIVEN a valid parsed bcl2fastq
    caplog.set_level(logging.INFO)
    # WHEN validating said "valid" report
    parsed_indexreport.validate()
    # THEN validations should be passed
    assert "Validation passed" in caplog.text


def test_write_report(validated_indexreport: IndexReport, caplog):
    """Test writing function of a summary"""

    # GIVEN a validated bcl2fastq report
    caplog.set_level(logging.INFO)
    # WHEN we compile the summary report
    validated_indexreport.write_summary()
    # THEN we should create a report and see the message
    assert "Wrote indexcheck report summary to" in caplog.text


def test_validate_wrong_header_rt1(indexreport_wrong_header_rt1, caplog):
    """Test validation of faulty headers in Report Table 1"""

    # GIVEN a corrupt bcl2fastq indexcheck report with faulty headers
    caplog.set_level(logging.ERROR)
    # WHEN the corrupt bcl2fastq indexcheck report is validated
    with pytest.raises(IndexReportError) as e:
        indexreport_wrong_header_rt1.validate()
    # THEN an exception is raised and a message is reported
    assert (
        f"The header in the cluster count sample table is not matching the\n"
        f"control headers. Check if they need correction"
    ) in caplog.text


def test_validate_missing_lanes_rt2(indexreport_missing_lanes_rt2, caplog):
    """Test the validation of missing lanes and thus structure in Report table 2"""

    # GIVEN a corrupt bcl2fastq indexcheck report with missing lanes
    caplog.set_level(logging.ERROR)
    # WHEN the corrupt bcl2fastq indexcheck report is validated
    with pytest.raises(IndexReportError) as e:
        indexreport_missing_lanes_rt2.validate()
    # THEN an report error should be raised and the following message prompted
    assert (
        f"Top unknown barcode table is not matching the reference, please check the report"
    ) in caplog.text
