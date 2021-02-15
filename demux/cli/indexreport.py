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
    "--dry-run", help="Dry of the function, will not write any report", is_flag=True
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
@click.option(
    "--run-parameters-path",
    type=str,
    required=True,
    help="Path to RunParameters.xml file for the flowcell"
)
def summary(
    cluster_counts: int,
    dry_run: bool,
    index_report_path: str,
    out_dir: str,
    run_parameters_path: str,
):
    """Create a summary of the indexcheck report, extracting information on samples with low number of clusters
    and the topmost common unknown indexes"""
    index_report = IndexReport(
        cluster_counts=cluster_counts,
        index_report_path=Path(index_report_path),
        out_dir=Path(out_dir),
        report_tables_index=report_tables_index,
        run_parameters_path=Path(run_parameters_path),
    )
    LOG.info(f"Creating summary of laneBarcode.html for FC: {index_report.flowcell_id}")
    index_report.validate(reference_report_header=reference_report_header)
    if not dry_run:
        index_report.write_summary(report_tables_index=report_tables_index)
    else:
        LOG.info("This is a dry-run, will not write a summary report")
