#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function, division
import sys
import os
from glob import glob
import logging
import socket
import yaml
from os.path import expanduser

from sqlalchemy import func
from clinstatsdb.db.store import connect
from clinstatsdb.db.models import Supportparams, Version, Datasource, Flowcell, Demux, Project, Sample, Unaligned
from clinstatsdb.utils import xstats

__version__ = '3.41.0'

logger = logging.getLogger(__name__)

class Config:

    def __init__(self):
        with open(expanduser("~/.clinical/databases.yaml"), 'r') as ymlfile:
            self.config = yaml.load(ymlfile)

    def __getitem__(self, key):
        """Simple array-based getter.

        Args:
            key (str): Gets the value for this key in the YAML file.

        Returns (str, dict): returns the structure underneat this key.

        """
        return self.config[key]

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
    logfilenames = glob(os.path.join(run_dir, 'LOG', 'Xdem-l?t??-*.log')) # should yield one result
    if len(logfilenames) == 0:
        logger.error('No log files found! Looking for %s', os.path.join(run_dir, 'LOG', 'Xdem-l?t??-*.log'))
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
        projects.append(os.path.basename(os.path.normpath(project_dir)).split('_')[1])

    return projects

def sanitize_sample(sample):
    """Removes the _nxdual9 index indication
    Removes the B (reprep) or F (reception fail) suffix from the sample name

    Args:
        sample (str): a sample name

    Return (str): a sanitized sample name

    """
    return sample.split('_')[0].rstrip('BF')

def get_sample_sheet(demux_dir):
    sample_sheet = []
    samplesheet_file_name = glob("{demux_dir}/SampleSheet.csv".format(demux_dir=demux_dir))[0]
    with open(samplesheet_file_name, 'r') as samplesheet_fh:
        lines = [ line.strip().split(',') for line in samplesheet_fh.readlines() ]
        header = []
        for line in lines:
            # skip headers
            if line[0].startswith('['): continue
            if line[2] == 'SampleID':
                header = line
                continue

            entry = dict(zip(header, line))
            sample_sheet.append(entry)

    return sample_sheet

def get_nr_samples_lane(sample_sheet):
    samples_lane = {}
    for line in sample_sheet:
        if line['Lane'] not in samples_lane:
             samples_lane[ line['Lane'] ] = 0
        samples_lane[ line['Lane'] ] += 1

    return samples_lane

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

    config = Config()
    SQL = connect(config['clinstats']['connection_string'])

    if not Version.check(config['clinstats']['name'], config['clinstats']['version']):
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

    datasource_id = Datasource.exists(os.path.join(demux_dir, 'l1t11/Stats/ConversionStats.xml'))
    if not datasource_id:
        new_datasource = gather_datasouce(demux_dir)
        datasource = Datasource()
        datasource.runname = new_datasource['runname']
        datasource.rundate = new_datasource['rundate']
        datasource.machine = new_datasource['machine']
        datasource.servername = new_datasource['servername']
        datasource.document_path = new_datasource['document_path']
        datasource.document_type = 'xml'
        datasource.time = func.now()
        datasource.supportparams_id = supportparams_id

        SQL.add(datasource)
        SQL.flush()
        datasource_id = datasource.datasource_id

    full_flowcell_name = os.path.basename(os.path.normpath(demux_dir)).split('_')[-1]
    flowcell_name = full_flowcell_name[1:]
    flowcell_pos  = full_flowcell_name[0]
    flowcell_id   = Flowcell.exists(flowcell_name)
    if not flowcell_id:
        flowcell = Flowcell()
        flowcell.flowcellname = flowcell_name
        flowcell.flowcell_pos = flowcell_pos
        flowcell.hiseqtype = 'hiseqx'
        flowcell.time = func.now()

        SQL.add(flowcell)
        SQL.flush()
        flowcell_id = flowcell.flowcell_id

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

    project_id_of = {} # project name: project id
    for project_name in get_projects(demux_dir):
        project_id = Project.exists(project_name)
        if not project_id:
            p = Project()
            p.projectname = project_name
            p.time = func.now()

            SQL.add(p)
            SQL.flush()
            project_id = p.project_id

        project_id_of[ project_name ] = project_id

    sample_sheet = get_sample_sheet(demux_dir)
    stats = xstats.parse(demux_dir)
    stats_samples = xstats.parse_samples(demux_dir)
    nr_samples_lane = get_nr_samples_lane(sample_sheet)
    for sample in sample_sheet:
        sample_id = Sample.exists(sample['SampleID'], sample['index'])
        if not sample_id:
            s = Sample()
            s.project_id = project_id_of[ sample['Project'] ]
            s.samplename = sample['SampleID']
            s.barcode = sample['index']
            s.time = func.now()

            SQL.add(s)
            SQL.flush()
            sample_id = s.sample_id

        if not Unaligned.exists(sample_id, demux_id, sample['Lane']):
            u = Unaligned()
            u.sample_id = sample_id
            u.demux_id = demux_id
            u.lane = sample['Lane']
            if nr_samples_lane[ sample['Lane'] ] > 1: # pooled!
                stats_sample = stats_samples[ sample['Lane'] ][ sample['SampleID'] ]

                u.yield_mb = round(int(stats_sample['pf_yield']) / 1000000, 2)
                u.passed_filter_pct = stats_sample['pf_yield_pc']
                u.readcounts = stats_sample['pf_clusters']
                u.raw_clusters_per_lane_pct = stats_sample['raw_clusters_pc']
                u.perfect_indexreads_pct = round(stats_sample['perfect_barcodes'] / stats_sample['barcodes'] * 100, 5)
                u.q30_bases_pct = stats_sample['pf_Q30']
                u.mean_quality_score = stats_sample['pf_qscore']
            else:
                u.yield_mb = round(int(stats[ sample['SampleID'] ]['pf_yield']) / 1000000, 2)
                u.passed_filter_pct = stats[ sample['SampleID'] ]['pf_yield_pc']
                u.readcounts = stats[ sample['SampleID'] ]['pf_clusters']
                u.raw_clusters_per_lane_pct = stats[ sample['SampleID'] ]['raw_clusters_pc']
                u.perfect_indexreads_pct = round(stats[ sample['SampleID'] ]['perfect_barcodes'] / stats[ sample['SampleID'] ]['barcodes'] * 100, 5)
                u.q30_bases_pct = stats[ sample['SampleID'] ]['pf_Q30']
                u.mean_quality_score = stats[ sample['SampleID'] ]['pf_qscore']
            u.time = func.now()

            SQL.add(u)

    SQL.flush()
    SQL.commit()

if __name__ == '__main__':
    main(sys.argv[1:])
