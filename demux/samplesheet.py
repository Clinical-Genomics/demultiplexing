# -*- coding: utf-8 -*-

import click
import logging

@click.group()
def samplesheet():
    """Samplesheet commands"""
    pass

@samplesheet.command()
def validate():
    """TODO: Docstring for validate.
    Returns: TODO

    """
    pass

@samplesheet.command()
def massage():
    """TODO: Docstring for massage.
    Returns: TODO

    """
    pass

@samplesheet.command()
def demux():
    """ Convert NIPT samplesheet to demux'able samplesheet """
    pass

samplesheet.add_command(validate)
samplesheet.add_command(massage)
samplesheet.add_command(demux)
