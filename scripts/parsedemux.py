#!/usr/bin/python
#
import sys
import os
import glob
import time
from access import db

"""Parses demux stats to db.
  usage: parsedemux.py  <BASEDIRECTORYforUNALIGNED> <UNALIGNEDsubdir> <samplesheetcsv> <config_file:optional>
Args:
  BASEDIRECTORYforUNALIGNED (str): path to demux directory
  UNALIGNEDsubdir (str): subdir with demux data structure
  pathtosamplesheetcsv (str): absolute path to samplesheet
Returns:
  Outputs what data have been added to database including row id for each table
"""

if (len(sys.argv)>4):
  configfile = sys.argv[4]
  if not os.path.isfile(configfile):
    exit("Bad configfile")
else:
  if len(sys.argv) == 4:
    configfile = 'None'
  else:
    print "usage: parsedemux.py <BASEDIRECTORYforUNALIGNED> <UNALIGNEDsubdir> <samplesheetcsv> <config_file:optional>"
    exit(1)
pars = db.readconfig(configfile)
basedir = sys.argv[1]
if not (basedir[-1:] == "/"):
  basedir = basedir + "/"
if not os.path.isdir(basedir):
  exit("Bad basedir")
unaligned = sys.argv[2]
if not (unaligned[-1:] == "/"):
  unaligned = unaligned + "/"
if not os.path.isdir(basedir + unaligned):
  exit("Bad unaligned dir")
samplesheet = sys.argv[3]
if not os.path.isfile(samplesheet):
  exit("Bad samplesheet")

print basedir, unaligned, samplesheet

with db.create_tunnel(pars['TUNNELCMD']):

  with db.dbconnect(pars['CLINICALDBHOST'], pars['CLINICALDBPORT'], pars['STATSDB'], 
                        pars['CLINICALDBUSER'], pars['CLINICALDBPASSWD']) as dbc:

    ver = dbc.versioncheck(pars['STATSDB'], pars['DBVERSION'])

    if not ver == 'True':
      print "Wrong db " + pars['STATSDB'] + " v:" + pars['DBVERSION']
      exit(0) 
    else:
      print "Correct db " + pars['STATSDB'] + " v:" + pars['DBVERSION']

    demux = (basedir + unaligned + "Basecall_Stats*")
    demux_stat_dir = glob.glob(demux)
    print demux_stat_dir
# read in run parameters from Unaligned/support.txt
    if not os.path.isfile(basedir + unaligned + "support.txt"):
      exit ("Bad support.txt")
    support = open(basedir + unaligned + "support.txt")
    support_lines = support.readlines()
    support.close()


    now = time.strftime('%Y-%m-%d %H:%M:%S')

    print now
