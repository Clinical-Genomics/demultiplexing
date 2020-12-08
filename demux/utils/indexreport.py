import codecs
import re

from bs4 import BeautifulSoup, ResultSet, Tag
from pathlib import Path


class IndexReport:
    """holds information on the indexcheck report created from bcl2fastq and manages its information"""

    def __init__(
        self,
        out_dir: Path,
        index_report_path: Path,
        flowcell_id: str,
        cluster_counts: int,
    ):

        self.out_dir = out_dir
        self.index_report_path = index_report_path
        self.flowcell_id = flowcell_id
        self.cluster_counts = cluster_counts

    def parse_report(self):
        """Parses bcl2fastq indexcheck report"""

        def _html_content():
            """Get the content of the report"""
            html_content = BeautifulSoup(self.index_report_path, "html.parser")
            self.html_content: BeautifulSoup = html_content

        def _report_tables():
            """Get the ReportTables inside the html report"""

            report_tables = self.html_content.find_all("table", id="ReportTable")
            self.report_tables: ResultSet = report_tables

        def _header_samples_table():
            """Get the header from the large table with all sample clusters"""

            headers = []
            header_indeces = {}

            indeces_counter = 0

            tmp_headers = self.report_tables[1].tr.find_all("th")

            for column in tmp_headers:
                column = re.sub("<br/>", "", str(column))
                column = re.sub("<.*?>", "", column)
                headers.append(column)
                header_indeces[column] = indeces_counter
                indeces_counter += 1

            self.raw_headers = self.report_tables[1].tr
            self.headers_report_tables: list = headers
            self.header_indeces: dict = header_indeces

        def _top_unknown_barcodes_table():
            """Get the table with the top unknown barcodes"""

            self.top_unknown_barcodes = self.report_tables[2]

        def _get_low_cluster_counts():
            """Find samples with low cluster counts, default count checked 1000000"""
            low_cluster_counts = []
            for row in self.report_tables[1].find_all("tr")[1:]:
                tmp_row = row.find_all("td")
                tmp_project = re.sub(
                    "<.*?>", "", str(tmp_row[self.header_indeces["Project"]])
                )
                tmp_cluster_count = re.sub(
                    "<.*?>", "", str(tmp_row[self.header_indeces["PF Clusters"]])
                )
                if tmp_project != "indexcheck":
                    if int(tmp_cluster_count.replace(",", "")) < self.cluster_counts:
                        low_cluster_counts.append(row)

            self.low_cluster_counts: list = low_cluster_counts

        _html_content()
        _report_tables()
        _header_samples_table()
        _top_unknown_barcodes_table()
        _get_low_cluster_counts()

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
