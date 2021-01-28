import click
import logging

from pathlib import Path

from demux.constants import reference_report_header, report_tables_index
from demux.utils.indexreport import IndexReport


LOG = logging.getLogger(__name__)


@click.group()
def indexreport():
    """Index report commands"""


@indexreport.command()
@click.option(
    "--cluster-counts",
    type=int,
    default=1000000,
    help=(
        f"Cluster count cut-off, any samples (besides indexcheck ones) with lower cluster counts are"
        f" included in the summary"
    ),
)
@click.option(
    "--flowcell-id",
    type=str,
    required=True,
    help="Flowcell id of given indexcheck report",
)
@click.option(
    "--index-report-path",
    type=str,
    required=True,
    help="Path to bcl2fastq indexcheck report (laneBarcode.html)",
)
@click.option(
    "--out-dir",
    type=str,
    required=True,
    help="Path of outdirectory for summary report",
)
def summary(
    cluster_counts: int, flowcell_id: str, index_report_path: str, out_dir: str
):
    """Create a summary of the indexcheck report, extracting information on samples with low number of clusters
    and the topmost common unknown indexes"""
    index_report = IndexReport(
        cluster_counts=cluster_counts,
        flowcell_id=flowcell_id,
        index_report_path=Path(index_report_path),
        out_dir=Path(out_dir),
        report_tables_index=report_tables_index,
    )
    LOG.info(f"Creating summary of laneBarcode.html for FC: {index_report.flowcell_id}")
    index_report.validate(reference_report_header=reference_report_header)
    index_report.write_summary(report_tables_index=report_tables_index)
