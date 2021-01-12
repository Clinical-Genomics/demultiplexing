import bs4
import re
import logging

from pathlib import Path

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
        INDEX_REPORT_HEADER: list,
    ):
        self.INDEX_REPORT_HEADER = INDEX_REPORT_HEADER
        self.out_dir = out_dir
        self.index_report_path = index_report_path
        self.flowcell_id = flowcell_id
        self.cluster_counts = cluster_counts

    def _html_content(self):
        """Get the content of the report"""

        with self.index_report_path.open() as f:
            html_content = bs4.BeautifulSoup(f, "html.parser")
            self.html_content: bs4.BeautifulSoup = html_content

    def _report_tables(self):
        """Get the ReportTables inside the html report"""

        report_tables = self.html_content.find_all("table", id="ReportTable")
        self.report_tables: bs4.ResultSet = report_tables

    def _header_samples_table(self):
        """Get the header from the large table with all sample clusters"""

        headers = []
        header_index = {}

        index_counter = 0
        raw_sample_headers = self.report_tables[1].tr.find_all("th")

        for column in raw_sample_headers:
            column = re.sub("<br/>", " ", str(column))
            column = re.sub("<.*?>", "", column)
            headers.append(column)
            header_index[column] = index_counter
            index_counter += 1

        self.raw_headers = self.report_tables[1].tr
        self.headers_report_tables: list = headers
        self.header_index: dict = header_index

    def _top_unknown_barcodes_table(self):
        """Get the table with the top unknown barcodes"""

        self.top_unknown_barcodes = self.report_tables[2]

    def _get_low_cluster_counts(self):
        """Find samples with low cluster counts"""

        low_cluster_counts = []

        for row in self.report_tables[1].find_all("tr")[1:]:
            project = re.sub(
                "<.*?>", "", str(row.find_all("td")[self.header_index["Project"]])
            )
            cluster_count = re.sub(
                "<.*?>", "", str(row.find_all("td")[self.header_index["PF Clusters"]])
            )
            if project != "indexcheck":
                if int(cluster_count.replace(",", "")) < self.cluster_counts:
                    low_cluster_counts.append(row)

        self.low_cluster_counts: list = low_cluster_counts

    def parse_report(self):
        """Parses bcl2fastq indexcheck report"""

        LOG.info(
            f"Parsing file {self.index_report_path}, extracting top unkown barcodes and samples with cluster"
            f"counts lower than {self.cluster_counts}"
        )

        self._html_content()
        self._report_tables()
        self._header_samples_table()
        self._top_unknown_barcodes_table()
        self._get_low_cluster_counts()
        LOG.info(f"Parsing complete!")

    def validate_report_tables(self):
        """ Validate the number of report tables """
        try:
            assert len(self.report_tables) == 3
        except AssertionError:
            LOG.error("The number of Report Tables are not the same")
            raise IndexReportError

    def validate_index_report_header(self):
        """ Validate the index report headers """

        try:
            assert self.INDEX_REPORT_HEADER == list(self.header_index.keys())
        except AssertionError as e:
            LOG.error(
                f"The header in the cluster count sample table is not matching the\n"
                f"control headers. Check if they need correction"
            )
            raise IndexReportError

    def validate_topunknown_barcodes_table(self):
        """ Validate the top unknown barcodes table """

        try:
            assert (
                len(
                    re.sub("<.*?>", "", str(self.report_tables[2].tr))
                    .strip()
                    .split("Lane")
                )
                == 5
            )
        except AssertionError as e:
            LOG.error(
                f"Top unkown barcode table is not matching the reference, please check the report"
            )
            raise IndexReportError

    def validate(self):
        """Validate report structure"""

        LOG.info(f"Validating report")
        self.validate_report_tables()
        self.validate_index_report_header()
        self.validate_topunknown_barcodes_table()
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
