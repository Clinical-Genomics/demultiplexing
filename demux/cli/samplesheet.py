# -*- coding: utf-8 -*-

import click
import logging

from cglims.api import ClinicalLims, ClinicalSample
from ..utils import Samplesheet

@click.group()
def samplesheet():
    """Samplesheet commands"""
    pass

@samplesheet.command()
@click.argument('samplesheet')
def validate(samplesheet):
    """validates a samplesheet"""
    Samplesheet(samplesheet).validate()

@samplesheet.command()
@click.argument('samplesheet')
def massage(samplesheet):
    """creates a NIPT ready SampleSheet"""
    print(Samplesheet(samplesheet).massage())

@samplesheet.command()
@click.argument('samplesheet')
def demux(samplesheet):
    """convert NIPT samplesheet to demux'able samplesheet """
    print(Samplesheet(samplesheet).to_demux())

@samplesheet.command()
@click.argument('flowcell')
@click.option('-m', '--machine', type=click.Choice(['X', '2500']), help='machine type')
@click.pass_context
def fetch(context, flowcell, machine, delim=',', end='\n'):
    """Fetch a samplesheet from LIMS"""

    def get_project(project):
        """ Only keeps the first part of the project name"""
        return project.split(' ')[0]

    lims_api = ClinicalLims(**context.obj['lims'])
    raw_samplesheet = lims_api.samplesheet(flowcell)

    # this is how the data is keyed when it gets back from LIMS
    lims_keys = ['FCID', 'Lane', 'SampleID', 'SampleRef', 'index', 'Description', 'Control', 'Recipe', 'Operator', 'Project']

    # ... this is the exact header we need for an X SampleSheet
    header = lims_keys
    if machine == '2500':
        # ... for a HiSeq2500, the header looks slightly different
        header = ['FCID', 'Lane', 'SampleID', 'SampleRef', 'Index', 'Description', 'Control', 'Recipe', 'Operator', 'SampleProject']

    click.echo(delim.join(header))
    for line in raw_samplesheet:
        # fix the project content
        line['Project'] = get_project(line['Project']) 

        # print it!
        click.echo(delim.join([str(line[head]) for head in lims_keys]))
