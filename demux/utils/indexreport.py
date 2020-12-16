import re
import bs4
import logging

from pathlib import Path

from demux.exc import IndexReportError


class IndexReport:
    """Indexcheck report class, able to hold and process information out of bcl2fastq html reports"""

    def __init__(
        self,
        out_dir: Path,
        index_report_path: Path,
        flowcell_id: str,
        cluster_counts: int,
        INDEX_REPORT_HEADER: list,
        log
    ):
        self.INDEX_REPORT_HEADER = INDEX_REPORT_HEADER
        self.out_dir = out_dir
        self.index_report_path = index_report_path
        self.flowcell_id = flowcell_id
        self.cluster_counts = cluster_counts
        self.log = log

    def _html_content(self):
        """Get the content of the report"""

        html_content = bs4.BeautifulSoup(self.index_report_path, "html.parser")
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

        tmp_headers = self.report_tables[1].tr.find_all("th")

        for column in tmp_headers:
            column = re.sub("<br/>", "", str(column))
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
            tmp_row = row.find_all("td")
            tmp_project = re.sub(
                "<.*?>", "", str(tmp_row[self.header_index["Project"]])
            )
            tmp_cluster_count = re.sub(
                "<.*?>", "", str(tmp_row[self.header_index["PF Clusters"]])
            )
            if tmp_project != "indexcheck":
                if int(tmp_cluster_count.replace(",", "")) < self.cluster_counts:
                    low_cluster_counts.append(row)

        self.low_cluster_counts: list = low_cluster_counts

    def parse_report(self):
        """Parses bcl2fastq indexcheck report"""

        self.log.info(
            f"Parsing file {self.index_report_path.name}, extracting top unkown barcodes and samples with cluster"
            f"counts lower than {self.cluster_counts}"
        )

        self._html_content()
        self._report_tables()
        self._header_samples_table()
        self._top_unknown_barcodes_table()
        self._get_low_cluster_counts()

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
            self.log.info(
                f"Wrote indexcheck report summary for "
                f"{self.flowcell_id} to {self.out_dir}/laneBarcode_summary.html"
            )

    def validate(self, INDEX_REPORT_HEADER):
        """Validate report structure"""

        try:
            self.log.info(f"Validating report")
            # Should contain 3
            assert len(self.report_tables) == 3
            # Headers in cluster count table should be the same as expected
            assert INDEX_REPORT_HEADER == list(self.header_index.keys())
            # Validating the table for top unknown barcodes
            # Column count instead of rows if varying number of top unknown barcodes
            assert len(re.sub("<.*?>", "", str(self.report_tables[2].tr)).strip().split('Lane')) == 5
        except AssertionError:
            raise IndexReportError("Check format of index report")
        self.log.info(f"Validation passed")
