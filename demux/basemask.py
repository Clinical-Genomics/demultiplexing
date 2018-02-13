# -*- coding: utf-8 -*-

import sys
import click
import logging

from path import Path
import xml.etree.cElementTree as et

from .utils import Samplesheet, HiSeqXSamplesheet, NIPTSamplesheet, HiSeq2500Samplesheet, MiseqSamplesheet

log = logging.getLogger(__name__)

@click.group()
def basemask():
    """Samplesheet commands"""
    pass

@basemask.command()
@click.argument('rundir')
@click.option('-l', '--lane', help='lane number')
@click.option('-a', '--application', type=click.Choice(['wgs', 'wes', 'nipt', 'miseq']), help='sequencing type')
def create(rundir, lane, application):
    """Create a basemask based on SampleSheet.csv and runParameters"""

    sheet = None
    samplesheet = Path(rundir).joinpath('SampleSheet.csv')
    if application == 'nipt':
        sheet = NIPTSamplesheet(samplesheet)
    elif application == 'wes':
        sheet = HiSeq2500Samplesheet(samplesheet)
    elif application == 'miseq':
        sheet = MiseqSamplesheet(samplesheet)
    elif application == 'wgs':
        sheet = HiSeqXSamplesheet(samplesheet)


    # runParameters.xml
    run_params_tree = et.parse(Path(rundir).joinpath('runParameters.xml'))
    read1_len = int(run_params_tree.findtext('Setup/IndexRead1'))
    read2_len = int(run_params_tree.findtext('Setup/IndexRead2'))

    lines = [line for line in sheet.lines_per_column('lane', lane)]
    
    # get the inex lengths
    first = lines[0]
    index1, *_ = first['index'].replace('+', '-').split('-')
    index2 = _[0] if len(_) > 0 else '' # ok, a bit weird. *_ is a catch all and returns a list.

    # index1 basemask
    i1n = 'n' * (read1_len - len(index1))
    i1 = 'I' + str(len(index1)) + i1n

    # index2 basemask
    if read2_len == 0:
        click.echo(f'Y151,{i1},Y151')
    else:
        if len(index2) > 0:
            i2 = ',I' + str(len(index2))
            click.echo(f'Y151,{i1}{i2},Y151')
        else: # suggestion from Illumina
            click.echo("'Y*,I*,I*,Y*'")
