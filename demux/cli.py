# -*- coding: utf-8 -*-
import logging
import click
import yaml

from .samplesheet import samplesheet

log = logging.getLogger(__name__)

__version__ = '3.42.7'


@click.group()
@click.option('-l', '--log-level', default='INFO', envvar='LOGLEVEL')
@click.option('-c', '--config', type=click.File('r'))
@click.version_option(version=__version__, prog_name="deliver")
@click.pass_context
def demux(context, log_level, config):
    """Making demuxing easier!"""
    setup_logging(level=log_level)
    log.info('{}: version {}'.format(__package__, __version__))
    context.obj = yaml.load(config) if config else {}
    context.obj['log_level'] = log_level


def setup_logging(level='INFO'):
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # customize formatter, align each column
    template = "[%(asctime)s] %(name)-25s %(levelname)-8s %(message)s"
    formatter = logging.Formatter(template)
    
    # add a basic STDERR handler to the logger
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)

    root_logger.addHandler(console)
    return root_logger

demux.add_command(samplesheet)
