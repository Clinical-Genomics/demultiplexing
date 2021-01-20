import bs4
import logging
import re

from pathlib import Path

from demux.constants import INDEX_REPORT_HEADER
from demux.exc import IndexReportError

LOG = logging.getLogger(__name__)


class IndexReport:
    """Indexcheck report class, able to hold and process information out of bcl2fastq html reports"""

    def __init__(
        self,
        out_dir: Path,
        index_report_path: Path,
        flowcell_id: str,
        cluster_counts: int,
    ):
        self.cluster_counts = cluster_counts
        self.flowcell_id = flowcell_id
        self.INDEX_REPORT_HEADER: list = INDEX_REPORT_HEADER
        self.index_report_path = index_report_path
        self.out_dir = out_dir

        LOG.info(
            f"Parsing file {self.index_report_path}, extracting top unkown barcodes and samples with cluster"
            f"counts lower than {self.cluster_counts}"
        )
        self.html_content = self._get_html_content()
        self.report_tables = self._get_report_tables()
        self.samples_table_header = self._get_sample_table_header()
        self.top_unknown_barcodes = self._get_top_unknown_barcodes_table()
        self.low_cluster_counts = self._get_low_cluster_counts()
        LOG.info(f"Parsing complete!")

    def _get_html_content(self) -> bs4.BeautifulSoup:
        """Get the content of the report"""

        with self.index_report_path.open() as f:
            html_content = bs4.BeautifulSoup(f, "html.parser")
            return html_content

    def _get_report_tables(self) -> bs4.ResultSet:
        """Get the ReportTables inside the html report"""

        html_content = self._get_html_content()
        report_tables = html_content.find_all("table", id="ReportTable")
        return report_tables

    def _get_sample_table_header(self) -> dict:
        """Get the header from the large table with all sample clusters"""

        report_tables = self._get_report_tables()

        header_index = {}

        raw_sample_headers = report_tables[1].tr.find_all("th")

        for index, html_column_header in enumerate(raw_sample_headers):
            header = purify_html_header(html_column_header)
            header_index[header] = index

        return header_index

    def _get_top_unknown_barcodes_table(self) -> bs4.element.Tag:
        """Get the table with the top unknown barcodes"""

        report_tables = self._get_report_tables()
        return report_tables[2]

    def _get_low_cluster_counts(self) -> list:
        """Find samples with low cluster counts"""

        report_tables = self._get_report_tables()
        sample_table_header = self._get_sample_table_header()
        low_cluster_counts = []

        for html_project_cluster_count in report_tables[1].find_all("tr")[1:]:
            project, cluster_count = purify_html_project_cluster_counts(
                project_row=html_project_cluster_count,
                header_indeces=sample_table_header,
            )
            if project != "indexcheck":
                if cluster_count < self.cluster_counts:
                    low_cluster_counts.append(html_project_cluster_count)

        return low_cluster_counts

    def validate(self):
        """Validate report structure"""

        LOG.info(f"Validating report")
        for valid, message in [
            validate_report_tables(report_tables=self.report_tables),
            validate_index_report_header(
                reference_header=self.INDEX_REPORT_HEADER,
                samples_table_header=self.samples_table_header,
            ),
            validate_top_unknown_barcodes_table(
                top_unknown_barcodes_table=self.top_unknown_barcodes
            ),
        ]:
            if not valid:
                LOG.error(message)
                raise IndexReportError
            elif valid:
                LOG.info(message)
        LOG.info(f"Validation passed")

    def write_summary(self):
        """Compile a summary report of the bcl2fastq report"""

        out_dir_path = Path(self.out_dir)

        with open((out_dir_path / "laneBarcode_summary.html"), "+w") as fo:
            fo.write(
                f"<h1>Flowcell summary: {self.flowcell_id}</h1>"
                f"<h2>Low cluster counts</h2>"
            )
            fo.write(f'<table border="1" ID="ReportTable">')
            fo.write(str(self.report_tables[1].tr))
            for row in self.low_cluster_counts:
                fo.write(str(row))
            fo.write(f"</table>")
            fo.write(str(self.html_content.find_all("h2")[2]))
            fo.write(str(self.top_unknown_barcodes))
        LOG.info(
            f"Wrote indexcheck report summary to {self.out_dir}/laneBarcode_summary.html"
        )


def purify_html_header(html_column_header) -> str:
    """Purify html header into a string without html syntax"""

    column_header = re.sub("<br/>", " ", str(html_column_header))
    header = re.sub("<.*?>", "", column_header)

    return header


def purify_html_project_cluster_counts(
    project_row: bs4.element.Tag, header_indeces: dict
) -> (str, int):
    """Purify a html project cluster count row from html syntax"""

    project = re.sub(
        "<.*?>", "", str(project_row.find_all("td")[header_indeces["Project"]])
    )
    cluster_count = re.sub(
        "<.*?>", "", str(project_row.find_all("td")[header_indeces["PF Clusters"]])
    )
    cluster_count = int(cluster_count.replace(",", ""))

    return project, cluster_count


def validate_top_unknown_barcodes_table(
    top_unknown_barcodes_table: bs4.element.Tag,
) -> (bool, str):
    """Validate the top unknown barcodes table, checking that all lanes are present"""

    try:
        assert (
            len(
                re.sub("<.*?>", "", str(top_unknown_barcodes_table.tr))
                .strip()
                .split("Lane")
            )
            == 5
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
    reference_header: list, samples_table_header: dict
) -> (bool, str):
    """Validate the index report headers"""

    try:
        assert reference_header == list(samples_table_header.keys())
    except AssertionError as e:
        message = (
            f"The header in the cluster count sample table is not matching the\n"
            f"control headers. Check if they need correction"
        )
        return False, message
    message = f"Sample cluster count headers: Passed!"
    return True, message
