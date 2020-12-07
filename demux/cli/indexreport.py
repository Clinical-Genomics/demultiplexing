import click
import logging

from ..utils.indexreport import IndexReport

log = logging.getLogger(__name__)


@click.group()
def indexreport():
    """Index report commands"""
    pass


@indexreport.command()
@click.option('-r',
              '--report-path',
              type=click.File(mode='r'),
              required=True,
              help='Relative path to laneBarcode.html report')
@click.option('-fd',
              '--flowcell-dir',
              type=click.Path(exists=True),
              required=True,
              help='Relative path to novaseq flowcell directory')
@click.option('-f',
              '--flowcell-id',
              type=str,
              required=True,
              help='Identifier of flowcell')
@click.option('-c',
              '--cluster-counts',
              type=int,
              default=1000000,
              help=(f'Cluster count cut-off, any samples (besides indexcheck ones) with lower cluster counts are'
                    f' included in the summary'))
def summary(report_path, flowcell_dir, flowcell_id, cluster_counts):
    """Create a summary of the indexcheck report, extracting information on samples with low number of clusters
    and the topmost common unkown indexes"""
    click.echo(f'Parsing laneBarcode.html for FC: {flowcell_id}')
    index_report = IndexReport(
        flowcell_dir=flowcell_dir,
        report_path=report_path,
        flowcell_id=flowcell_id,
        cluster_counts=cluster_counts
    )
    index_report.parse_report()
    index_report.write_summary()
