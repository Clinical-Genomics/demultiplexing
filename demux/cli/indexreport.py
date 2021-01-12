import click
import logging

from demux.constants import INDEX_REPORT_HEADER
from demux.utils.indexreport import IndexReport
from pathlib import Path

LOG = logging.getLogger(__name__)


@click.group()
def indexreport():
    """Index report commands"""


@indexreport.command()
@click.option(
    "--index-report-path",
    type=str,
    required=True,
    help="Relative path to bcl2fastq indexcheck report (laneBarcode.html)",
)
@click.option(
    "--out-dir",
    type=str,
    required=True,
    help="Absolute path of terminal directory for summary report",
)
@click.option(
    "--flowcell-id",
    type=str,
    required=True,
    help="Flowcell id of given indexcheck report",
)
@click.option(
    "--cluster-counts",
    type=int,
    default=1000000,
    help=(
        f"Cluster count cut-off, any samples (besides indexcheck ones) with lower cluster counts are"
        f" included in the summary"
    ),
)
def summary(index_report_path: str, out_dir: str, flowcell_id: str, cluster_counts: int):
    """Create a summary of the indexcheck report, extracting information on samples with low number of clusters
    and the topmost common unkown indexes"""
    index_report = IndexReport(
        out_dir=Path(out_dir),
        index_report_path=Path(index_report_path),
        flowcell_id=flowcell_id,
        cluster_counts=cluster_counts,
        INDEX_REPORT_HEADER=INDEX_REPORT_HEADER,
    )
    LOG.info(f"Creating summary of laneBarcode.html for FC: {index_report.flowcell_id}")
    index_report.parse_report()
    index_report.validate()
    index_report.write_summary()
