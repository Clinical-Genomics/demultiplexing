# -*- coding: utf-8 -*-

import click
import logging

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
