import bs4
import logging
import re

from pathlib import Path

from demux.utils.html import (
    get_low_cluster_counts,
    get_html_content,
    get_report_tables,
    get_sample_table_header,
    get_top_unknown_barcodes_table,
)

from demux.exc import IndexReportError

LOG = logging.getLogger(__name__)


class IndexReport:
    """Indexcheck report class, able to hold and process information out of bcl2fastq html reports"""

    def __init__(
        self,
        cluster_counts: int,
        flowcell_id: str,
        index_report_path: Path,
        out_dir: Path,
        report_tables_index: dict,
    ):
        self.flowcell_id = flowcell_id
        self.index_report_path = index_report_path
        self.out_dir = out_dir

        LOG.info(
            f"Parsing file {index_report_path}, extracting top unknown barcodes and samples with cluster"
            f"counts lower than {cluster_counts}"
        )
        self.html_content = get_html_content(index_report_path=index_report_path)
        self.report_tables = get_report_tables(html_content=self.html_content)
        self.samples_table_header = get_sample_table_header(
            report_tables=self.report_tables, report_tables_index=report_tables_index
        )
        self.low_cluster_counts = get_low_cluster_counts(
            report_tables=self.report_tables,
            sample_table_header=self.samples_table_header,
            report_tables_index=report_tables_index,
            cluster_counts=cluster_counts,
        )
        self.top_unknown_barcodes = get_top_unknown_barcodes_table(
            report_tables=self.report_tables, report_tables_index=report_tables_index
        )
        LOG.info(f"Parsing complete!")

    def validate(self, reference_report_header: list):
        """Validate report structure"""

        LOG.info(f"Validating report")
        for valid, message in [
            validate_report_tables(report_tables=self.report_tables),
            validate_index_report_header(
                reference_header=reference_report_header,
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
