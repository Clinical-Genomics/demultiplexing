import bs4
import logging
import re

import xml.etree.cElementTree as Et

from pathlib import Path

from demux.constants.indexreport import flowcell_version_lane_count
from demux.utils.html import (
    get_html_content,
    parse_html_header,
    parse_html_project_cluster_counts,
)

from demux.exc import IndexReportError

LOG = logging.getLogger(__name__)


class IndexReport:
    """Indexcheck report class, able to hold and process information out of bcl2fastq html reports"""

    def __init__(
        self,
        cluster_counts: int,
        index_report_path: Path,
        out_dir: Path,
        report_tables_index: dict,
        run_parameters_path: Path,
    ):
        self.flowcell_id = find_flowcell_id(run_parameters_path=run_parameters_path)
        self.flowcell_version = find_flowcell_version(run_parameters_path=run_parameters_path)
        self.index_report_path = index_report_path
        self.out_dir = out_dir
        self.run_parameters = run_parameters_path

        LOG.info(
            f"Parsing file {index_report_path}, extracting top unknown barcodes and samples with cluster"
            f"counts lower than {cluster_counts}"
        )
        self.html_content = get_html_content(index_report_path=index_report_path)
        self.report_tables = self.get_report_tables(html_content=self.html_content)
        self.sample_table_header = self.get_sample_table_header(
            report_tables=self.report_tables, report_tables_index=report_tables_index
        )
        self.low_cluster_counts = self.get_low_cluster_counts(
            report_tables=self.report_tables,
            sample_table_header=self.sample_table_header,
            report_tables_index=report_tables_index,
            cluster_counts=cluster_counts,
        )
        self.top_unknown_barcodes = self.get_top_unknown_barcodes_table(
            report_tables=self.report_tables, report_tables_index=report_tables_index
        )
        LOG.info(f"Parsing complete!")

    @staticmethod
    def get_report_tables(html_content: bs4.BeautifulSoup) -> bs4.ResultSet:
        """Get the ReportTables inside the html report"""

        report_tables = html_content.find_all("table", id="ReportTable")
        return report_tables

    @staticmethod
    def get_sample_table_header(
        report_tables: bs4.ResultSet, report_tables_index: dict
    ) -> dict:
        """Get the header from the large table with all sample clusters"""

        header_index = {}

        html_sample_headers = report_tables[
            report_tables_index["cluster_count_table"]
        ].tr.find_all("th")

        for index, html_column_header in enumerate(html_sample_headers):
            header = parse_html_header(html_column_header)
            header_index[header] = index

        return header_index

    @staticmethod
    def get_low_cluster_counts(
        cluster_counts: int,
        report_tables: bs4.ResultSet,
        report_tables_index: dict,
        sample_table_header: dict,
    ) -> list:
        """Find samples with low cluster counts"""

        low_cluster_counts = []

        for html_project_cluster_count in report_tables[
            report_tables_index["cluster_count_table"]
        ].find_all("tr")[1:]:
            project, cluster_count = parse_html_project_cluster_counts(
                project_row=html_project_cluster_count,
                header_index=sample_table_header,
            )
            if project != "indexcheck":
                if cluster_count < cluster_counts:
                    low_cluster_counts.append(html_project_cluster_count)

        return low_cluster_counts

    @staticmethod
    def get_top_unknown_barcodes_table(
        report_tables: bs4.ResultSet, report_tables_index: dict
    ) -> bs4.element.Tag:
        """Get the table with the top unknown barcodes"""

        return report_tables[report_tables_index["top_unknown_barcode_table"]]

    def validate(self, reference_report_header: list):
        """Validate report structure"""

        LOG.info(f"Validating report")
        for valid, message in [
            validate_report_tables(report_tables=self.report_tables),
            validate_index_report_header(
                reference_header=reference_report_header,
                sample_table_header=self.sample_table_header,
            ),
            validate_top_unknown_barcodes_table(
                top_unknown_barcodes_table=self.top_unknown_barcodes, flowcell_version=self.flowcell_version
            ),
        ]:
            if not valid:
                LOG.error(message)
                raise IndexReportError
            elif valid:
                LOG.info(message)
        LOG.info(f"Validation passed")

    def write_summary(self, report_tables_index: dict):
        """Compile a summary report of the bcl2fastq report"""

        out_dir_path = Path(self.out_dir)

        with open((out_dir_path / "laneBarcode_summary.html"), "+w") as fo:
            fo.write(
                f"<h1>Flowcell summary: {self.flowcell_id}</h1>"
                f"<h2>Low cluster counts</h2>"
            )
            fo.write(f'<table border="1" ID="ReportTable">')
            fo.write(
                str(self.report_tables[report_tables_index["cluster_count_table"]].tr)
            )
            for row in self.low_cluster_counts:
                fo.write(str(row))
            fo.write(f"</table>")
            fo.write(
                str(
                    self.html_content.find_all("h2")[
                        report_tables_index["top_unknown_barcode_table"]
                    ]
                )
            )
            fo.write(str(self.top_unknown_barcodes))
        LOG.info(
            f"Wrote indexcheck report summary to {self.out_dir}/laneBarcode_summary.html"
        )


def find_flowcell_id(run_parameters_path: Path) -> str:
    """Parse the RunParameters.xml file and retrieve flowcell ID"""
    root = Et.parse(
        '/Users/karl.nyren/PycharmProjects/demultiplexing/tests/fixtures/novaseq/S4_RunParameters.xml').getroot()

    flowcell_id = root.find('ExperimentName').text

    return flowcell_id


def find_flowcell_version(run_parameters_path: Path) -> str:
    """Parse the RunParameters.xml file and retrieve flowcell version, e.g. S4, S1"""
    root = Et.parse('/Users/karl.nyren/PycharmProjects/demultiplexing/tests/fixtures/novaseq/S4_RunParameters.xml').getroot()

    rf_info = root.iter('RfidsInfo')

    for info in rf_info:
        flowcell_version = info.find('FlowCellMode').text

        return flowcell_version


def validate_top_unknown_barcodes_table(
        top_unknown_barcodes_table: bs4.element.Tag,
        flowcell_version: str
) -> (bool, str):
    """Validate the top unknown barcodes table, checking that all lanes are present"""
    print(flowcell_version)
    try:
        assert (
            len(
                re.sub("<.*?>", "", str(top_unknown_barcodes_table.tr))
                .strip()
                .split("Lane")
            )
            == flowcell_version_lane_count[flowcell_version] + 1
        )
    except AssertionError as e:
        message = f"Top unknown barcode table is not matching the reference, please check the report"
        return False, message
    message = "Top Unknown Barcodes table: Passed!"
    return True, message


def validate_report_tables(report_tables: bs4.ResultSet) -> (bool, str):
    """Validate the number of report tables"""
    try:
        assert len(report_tables) == 3
    except AssertionError:
        message = "The number of Report Tables are not the same"
        return False, message
    message = "Number of report tables: Passed!"
    return True, message


def validate_index_report_header(
    reference_header: list, sample_table_header: dict
) -> (bool, str):
    """Validate the index report headers"""

    try:
        assert reference_header == list(sample_table_header.keys())
    except AssertionError as e:
        message = (
            f"The header in the cluster count sample table is not matching the\n"
            f"control headers. Check if they need correction"
        )
        return False, message
    message = f"Sample cluster count headers: Passed!"
    return True, message
