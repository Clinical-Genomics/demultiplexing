#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function
import sys
import os
from glob import glob
import logging
import socket
import time

from sqlalchemy import func
from clinstatsdb.db import SQL
from clinstatsdb.db.models import Supportparams, Version, Datasource, Flowcell, Demux, Project

__version__ = '3.27.0'

logger = logging.getLogger(__name__)

def gather_supportparams(run_dir):
    """Aggregates all the support params:
    - bcl2fastq version
    - bcl2fastq path
    - command executed
    - datetime
    - SampleSheet.csv path
    - SampleSheet
    - DEMUX path

    Args:
        run_dir (str): FQPN run dir

    Returns: dict(
        'document_path',
        'idstring',
        'program',
        'commandline',
        'sampleconfig_path',
        'sampleconfig',
        'time')
    """

    rs = {} # result set

    # get some info from bcl2 fastq
    logfilenames = glob(os.path.join(run_dir, 'LOG', 'Xdem-l1t11-*.log')) # should yield one result
    if len(logfilenames) == 0:
        logger.error('No log files found! Looking for %s', os.path.join(run_dir, 'LOG', 'Xdem-l1t11-*.log'))
        exit(1)

    with open(logfilenames[0], 'r') as logfile:
        for line in logfile.readlines():
            if 'bcl2fastq v' in line:
                rs['idstring'] = line.strip()

            if '--use-bases-mask' in line:
                line = line.strip()
                split_line = line.split(' ')
                rs['commandline'] = ' '.join(split_line[1:]) # remove the leading [date]
                rs['time'] = split_line[0].strip('[]') # remove the brackets around the date
                rs['program'] = split_line[1] # get the executed program

    # get the sample sheet and it's contents
    samplesheet_path = os.path.join(run_dir, 'SampleSheet.csv')
    rs['sampleconfig_path'] = samplesheet_path
    rs['sampleconfig'] = ''.join(open(samplesheet_path, 'r').readlines())

    # get the unaligned dir
    document_path = os.path.join(run_dir, 'Unaligned')
    if not os.path.isdir(document_path):
        logger.error("Unaligned dir not found at '%s'", document_path)
        exit(1)
    else:
        rs['document_path'] = document_path

    return rs

def gather_datasouce(run_dir):
    """TODO: Docstring for gather_datasouce.

    Args:
        run_dir (TODO): TODO

    Returns: TODO

    """

    rs = {} # result set

    # get the run name
    rs['runname'] = os.path.basename(os.path.normpath(run_dir))

    # get the run date
    rs['rundate'] = rs['runname'].split('_')[0]

    # get the machine name
    rs['machine'] = rs['runname'].split('_')[1]

    # get the server name on which the demux took place
    rs['servername'] = socket.gethostname()

    # get the stats file
    document_path = os.path.join(run_dir, 'l1t11/Stats/ConversionStats.xml')
    if not os.path.isfile(document_path):
        logger.error("Stats file not found at '%s'", document_path)
        exit(1)
    else:
        rs['document_path'] = document_path

    return rs

def gather_flowcell(demux_dir):
    """TODO: Docstring for gather_flowcell.

    Args:
        demux_dir (TODO): TODO

    Returns: TODO

    """

    rs = {} # result set

    # get the flowcell name
    full_flowcell_name = os.path.basename(os.path.normpath(demux_dir)).split('_')[-1]
    rs['flowcellname'] = full_flowcell_name[1:]

    # get the flowcell position: A|B
    rs['flowcell_pos'] = full_flowcell_name[0]

    return rs

def gather_demux(demux_dir):
    """TODO: Docstring for gather_demux.

    Args:
        demux_dir (TODO): TODO

    Returns: TODO

    """

    rs = {} # result set

    # get some info from bcl2 fastq
    logfilenames = glob(os.path.join(demux_dir, 'LOG', 'Xdem-l1t11-*.log')) # should yield one result
    if len(logfilenames) == 0:
        logger.error('No log files found! Looking for %s', os.path.join(demux_dir, 'LOG', 'Xdem-l1t11-*.log'))
        exit(1)

    with open(logfilenames[0], 'r') as logfile:
        for line in logfile.readlines():

            if '--use-bases-mask' in line:
                line = line.strip()
                split_line = line.split(' ')
                basemask_params_pos = [i for i,x in enumerate(split_line) if x == '--use-bases-mask'][0]
                rs['basemask'] = split_line[basemask_params_pos + 1]

    return rs

def get_projects(demux_dir):
    """TODO: Docstring for get_projects.

    Args:
        demux_dir (TODO): TODO

    Returns: TODO

    """

    projects = []

    project_dirs = glob(os.path.join(demux_dir, 'Unaligned', '*'))
    for project_dir in project_dirs:
        projects.append(project_dir.split('_')[0])

    return projects

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

def main(argv):

    setup_logging(level='DEBUG')
    demux_dir = argv[0]

    if not Version.latest():
        logger.error('Wrong database!')
        exit(1)

    # ok, let's process the support params
    supportparams_id = Supportparams.exists(os.path.join(demux_dir, 'Unaligned'))
    if not supportparams_id:
        new_supportparams = gather_supportparams(demux_dir)
        supportparams = Supportparams()
        supportparams.document_path = new_supportparams['document_path']
        supportparams.idstring = new_supportparams['idstring']
        supportparams.program = new_supportparams['program']
        supportparams.commandline = new_supportparams['commandline']
        supportparams.sampleconfig_path = new_supportparams['sampleconfig_path']
        supportparams.sampleconfig = new_supportparams['sampleconfig']
        supportparams.time = new_supportparams['time']

        SQL.add(supportparams)
        SQL.flush()
        supportparams_id = supportparams.supportparams_id

    print(supportparams_id)

    datasource_id = Datasource.exists(os.path.join(demux_dir, 'l1t11/Stats/ConversionStats.xml'))
    if not datasource_id:
        new_datasource = gather_datasouce(demux_dir)
        datasource = Datasource()
        datasource.runname = new_datasource['runname']
        datasource.rundate = new_datasource['rundate']
        datasource.machine = new_datasource['machine']
        datasource.servername = new_datasource['servername']
        datasource.document_path = new_datasource['document_path']
        datasource.time = func.now()
        datasource.supportparams_id = supportparams_id

        SQL.add(datasource)
        SQL.flush()
        datasource_id = datasource.datasource_id

    print(datasource_id)

    full_flowcell_name = os.path.basename(os.path.normpath(demux_dir)).split('_')[-1]
    flowcell_name = full_flowcell_name[1:]
    flowcell_pos  = full_flowcell_name[0]
    flowcell_id   = Flowcell.exists(flowcell_name)
    if not flowcell_id:
        flowcell = Flowcell()
        flowcell.flowcellname = flowcell_name
        flowcell.flowcell_pos = flowcell_pos
        flowcell.time = func.now()

        SQL.add(flowcell)
        SQL.flush()
        flowcell_id = flowcell.flowcell_id

    print(flowcell_id)

    new_demux = gather_demux(demux_dir)
    demux_id = Demux.exists(flowcell_id, new_demux['basemask'])
    if not demux_id:
        demux = Demux()
        demux.flowcell_id = flowcell_id
        demux.datasource_id = datasource_id
        demux.basemask = new_demux['basemask']
        demux.time = func.now()

        SQL.add(demux)
        SQL.flush()
        demux_id = demux.demux_id
    
    print(demux_id)

    for project_name in get_projects(demux_dir):
        project_id = Project.exists(project_name)
        if not project_id:
            project = Project()
            project.projectname = project_name
            project.time = func.now()

            SQL.add(project)
            SQL.flush()
            project_id = project.project_id
            project = None

        print(project_id)


    SQL.rollback()

if __name__ == '__main__':
    main(sys.argv[1:])
