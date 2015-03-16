#!/usr/bin/python
#
import sys
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
else:
  if len(sys.argv) == 4:
    configfile = 'None'
  else:
    print "usage: parsedemux.py <BASEDIRECTORYforUNALIGNED> <UNALIGNEDsubdir> <samplesheetcsv> <config_file:optional>"
    sys.exit
pars = db.readconfig(configfile)
basedir = sys.argv[1]
unaligned = sys.argv[2]
samplesheet = sys.argv[3]

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

