# -*- coding: utf-8 -*-

import click
import logging

from cglims.api import ClinicalLims, ClinicalSample
from ..utils import Samplesheet, NIPTSamplesheet, HiSeq2500Samplesheet

@click.group()
def sheet():
    """Samplesheet commands"""
    pass

@sheet.command()
@click.argument('samplesheet')
@click.option('-a', '--application', type=click.Choice(['wgs', 'wes', 'nipt']), help='sequencing type')
def validate(samplesheet, application):
    """validate a samplesheet"""
    if application == 'nipt':
        NIPTSamplesheet(samplesheet).validate()
    elif application == 'wes':
        HiSeq2500Samplesheet(samplesheet).validate()
    else:
        Samplesheet(samplesheet).validate()

@sheet.command()
@click.argument('samplesheet')
def massage(samplesheet):
    """create a NIPT ready SampleSheet"""
    click.echo(NIPTSamplesheet(samplesheet).massage())

@sheet.command()
@click.argument('samplesheet')
def demux(samplesheet):
    """convert NIPT samplesheet to demux'able samplesheet """
    click.echo(NIPTSamplesheet(samplesheet).to_demux())

@sheet.command()
@click.argument('flowcell')
@click.option('-a', '--application', type=click.Choice(['wgs', 'wes']), help='application type')
@click.option('-d', '--delimiter', default=',', show_default=True, help='column delimiter')
@click.option('-e', '--end', default='\n', show_default=True, help='line delimiter')
@click.pass_context
def fetch(context, flowcell, application, delimiter=',', end='\n'):
    """Fetch a samplesheet from LIMS"""

    def get_project(project):
        """ Only keeps the first part of the project name"""
        return project.split(' ')[0]

    lims_api = ClinicalLims(**context.obj['lims'])
    raw_samplesheet = list(lims_api.samplesheet(flowcell))

    # this is how the data is keyed when it gets back from LIMS
    lims_keys = ['fcid', 'lane', 'sample_id', 'sample_ref', 'index', 'sample_name', 'control', 'recipe', 'operator', 'project']

    # ... fix some 2500 specifics
    if application == 'wes':
        header = [ HiSeq2500Samplesheet.header_map[head] for head in lims_keys ]

    # ... fix some X specifics
    if application == 'wgs':
        header = [ Samplesheet.header_map[head] for head in lims_keys ]
        for i, line in enumerate(raw_samplesheet):
            index = line['index'].split('-')[0]
            raw_samplesheet[i]['index'] = index
            raw_samplesheet[i]['sample_id'] = '{}_{}'.format(line['sample_id'], index)

    click.echo(delimiter.join(header))
    for line in raw_samplesheet:
        # fix the project content
        project = get_project(line['project']) 
        line['project'] = project
        line['sample_name'] = project

        # print it!
        click.echo(delimiter.join([str(line[head]) for head in lims_keys]))
