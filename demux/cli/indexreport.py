import click
import logging

from demux.utils.indexreport import IndexReport
from demux.constants import INDEX_REPORT_HEADER

log = logging.getLogger(__name__)


@click.group()
def indexreport():
    """Index report commands"""
    pass


@indexreport.command()
@click.option(
    "-i",
    "--index-report-path",
    type=click.File(mode="r"),
    required=True,
    help="Relative path to bcl2fastq indexcheck report (laneBarcode.html)",
)
@click.option(
    "-o",
    "--out-dir",
    type=click.Path(exists=True),
    required=True,
    help="Relative path to the output directory",
)
@click.option(
    "-f",
    "--flowcell-id",
    type=str,
    required=True,
    help="Flowcell id of given indexcheck report",
)
@click.option(
    "-c",
    "--cluster-counts",
    type=int,
    default=1000000,
    help=(
        f"Cluster count cut-off, any samples (besides indexcheck ones) with lower cluster counts are"
        f" included in the summary"
    ),
)
def summary(index_report_path, out_dir, flowcell_id, cluster_counts):
    """Create a summary of the indexcheck report, extracting information on samples with low number of clusters
    and the topmost common unkown indexes"""
    index_report = IndexReport(
        out_dir=out_dir,
        index_report_path=index_report_path,
        flowcell_id=flowcell_id,
        cluster_counts=cluster_counts,
        INDEX_REPORT_HEADER=INDEX_REPORT_HEADER,
    )
    click.echo(
        f"Creating summary of laneBarcode.html for FC: {index_report.flowcell_id}"
    )
    index_report.parse_report()
    index_report.validate()
    index_report.write_summary()
