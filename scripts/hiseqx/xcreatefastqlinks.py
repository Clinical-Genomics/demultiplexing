#!/usr/bin/python
#

from __future__ import print_function
import sys
import glob
import re
import os
from access import db, lims

__version__ = '3.7.0'

def getsamplesfromflowcell(demuxdir, flwc):
  samples = glob.glob("{demuxdir}*{flowcell}*/l?t??/Project_*/Sample_*".\
    format(demuxdir=demuxdir, flowcell=flwc))
  fc_samples = {}
  for sample in samples:
    sample = sample.split("/")[-1].split("_")[1]
    sample = sample.rstrip('BF') # remove the reprep (B) and reception control fail (F) letters from the samplename
    fc_samples[sample] = ''
  return fc_samples

def get_indexes(demuxdir, flwc):

  indexes = {} # sample_name: index
  samplesheet_file_name = glob.glob("{demuxdir}*{flowcell}*/SampleSheet.csv".\
    format(demuxdir=demuxdir, flowcell=flwc))[0]
  with open(samplesheet_file_name, 'r') as samplesheet_fh:
    lines = [ line.split(',') for line in samplesheet_fh.readlines() ]
    for line in lines:
      # skip headers
      if line[0].startswith('['): continue

      # ADM1003A4_dual90
      indexes[ line[2].split('_')[0] ] = line[4] # only take the sane sample name
    
  return indexes

def make_link(demuxdir, outputdir, family_id, cust_name, sample_name, fc, index):
    fastqfiles = glob.glob(
        "{demuxdir}*{fc}*/l?t??/Project_*/Sample_{sample_name}_*/*fastq.gz".format(
          demuxdir=demuxdir, fc=fc, sample_name=sample_name
        ))
    fastqfiles.extend(glob.glob(
        "{demuxdir}*{fc}*/l?t??/Project_*/Sample_{sample_name}[BF]_*/*fastq.gz".format(
          demuxdir=demuxdir, fc=fc, sample_name=sample_name
        )))
  
    for fastqfile in fastqfiles:
	print('Creating link for {}'.format(fastqfile))
        nameparts = fastqfile.split("/")[-1].split("_")
        rundir = fastqfile.split("/")[6]
	tile = fastqfile.split("/")[7].split('t')[1]
        date = rundir.split("_")[0]
        fc = rundir[-9:] + '-' + tile
        newname = "{lane}_{date}_{fc}_{sample_name}_{index}_{readdirection}.fastq.gz".format(
          lane=nameparts[2][-1:],
          date=date,
          fc=fc,
          sample_name=sample_name,
          index=index,
          readdirection=nameparts[3][-1:]
        )
  
        if cust_name != None and family_id != None:
            try:
                os.symlink(fastqfile, os.path.join(os.path.join(outputdir, cust_name, family_id, 'genomes', sample_name, 'fastq', newname)))
            except:
                print("Can't create symlink for {} in {}".format(sample_name, os.path.join(os.path.join(outputdir, cust_name, family_id, 'genomes', sample_name, 'fastq', newname))))

def main(argv):

  print(__version__)

  outputdir = '/mnt/hds/proj/bioinfo/MIP_ANALYSIS/'
  
  fc = None
  if len(argv) > 0:
    try:
      argv[0]
    except NameError:
      sys.exit("Usage: {} <flowcell name>".format(__file__))
    else:
      fc = argv[0]
  else:
    sys.exit("Usage: {} <flowcell name>".format(__file__))

  params = db.readconfig("non")
  smpls = getsamplesfromflowcell(params['DEMUXDIR'], fc)

  for sample in smpls.iterkeys():
    family_id = None
    cust_name = None
    with lims.limsconnect(params['apiuser'], params['apipass'], params['baseuri']) as lmc:
      analysistype = lmc.getattribute('samples', sample, "Sequencing Analysis")
      if analysistype is None:
        print("WARNING: Sequencing Analysis tag not defined for {}".format(sample))
        # skip to the next sample
        continue
      readcounts = .75 * float(analysistype[-3:])    # Accepted readcount is 75% of ordered million reads
      family_id = lmc.getattribute('samples', sample, 'familyID')
      cust_name = lmc.getattribute('samples', sample, 'customer')
      if not re.match(r'cust\d{3}', cust_name):
        print("WARNING '{}' does not match an internal customer name".format(cust_name))
        cust_name = None
      if cust_name == None:
        print("WARNING '{}' internal customer name is not set".format(sample))
      if family_id == None:
        print("WARNING '{}' family_id is not set".format(sample))

    indexes = get_indexes(params['DEMUXDIR'], fc)

    if readcounts:
      # try to create new dir structure
      if cust_name != None and family_id != None:
        try:
          os.makedirs(os.path.join(outputdir, cust_name, family_id, 'genomes', sample, 'fastq'))
        except OSError:
          pass
        try:
          os.makedirs(os.path.join(outputdir, cust_name, family_id, 'genomes', family_id))
        except OSError:
          pass

      # create symlinks for each fastq file
      make_link(
        demuxdir=params['DEMUXDIR'],
        outputdir=outputdir,
        family_id=family_id,
        cust_name=cust_name,
        sample_name=sample,
        fc=fc,
        index=indexes[sample]
      )
    else:
      print("{} - no analysis parameter specified in lims".format(sample))

if __name__ == '__main__':
  main(sys.argv[1:])
