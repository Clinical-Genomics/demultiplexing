"""Demultiplexing base demux command"""

import click
import coloredlogs
import logging
import yaml

from .basemask import basemask
from demux import __version__
from .indexreport import indexreport
from .samplesheet import sheet

LOG = logging.getLogger(__name__)
LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]


@click.group()
@click.option(
    "-l",
    "--log-level",
    type=click.Choice(LEVELS),
    default="INFO",
    help="Lowest level to log at",
)
@click.option("-c", "--config", type=click.File("r"))
@click.version_option(__version__)
@click.pass_context
def demux(context, log_level, config):
    """Making demultiplexing easier!"""

    coloredlogs.install(level=log_level)
    context.obj = yaml.full_load(config) if config else {}
    context.obj["log_level"] = log_level


demux.add_command(sheet)
demux.add_command(basemask)
demux.add_command(indexreport)
