import pytest
import logging

from demux.exc import IndexReportError
from demux.utils.indexreport import IndexReport

LOG = logging.getLogger(__name__)


def test_parse_indexreport(valid_indexreport: IndexReport, caplog):
    """ Test the function to parse a bcl2fastq indextcheck html report """

    caplog.set_level(logging.INFO)

    valid_indexreport.parse_report()

    assert "Parsing complete!" in caplog.text


def test_validate_valid_indexreport(parsed_valid_indexreport: IndexReport, caplog):
    """ Test validation on valid indexcheck report """

    caplog.set_level(logging.INFO)

    parsed_valid_indexreport.validate()

    assert "Validation passed" in caplog.text


def test_validate_wrong_header_rt1(indexreport_wrong_header_rt1, caplog):
    """ Test validation of faulty headers in Report Table 1 """

    caplog.set_level(logging.INFO)

    with pytest.raises(IndexReportError) as e:
        indexreport_wrong_header_rt1.validate()

    print(e)
    assert "Check format of index report" == str(e.value)


def test_write_report(validated_indexreport: IndexReport, caplog):
    """ Test writing function of a summary """

    caplog.set_level(logging.INFO)

    validated_indexreport.write_summary()

    assert "Wrote indexcheck report summary to" in caplog.text


# test write function
# test validation function
