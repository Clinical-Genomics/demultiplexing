#!/usr/bin/python
#
import sys
from access import db

"""Parses demux stats to db.
  usage: parsedemux.py  <BASEDIRECTORYforUNALIGNED> <absolutepathtosamplesheetcsv> <config_file:optional>"
Args:
  BASEDIRECTORYforUNALIGNED (str): path to demux directory
  absolutepathtosamplesheetcsv (str): path to samplesheet
Returns:
  Outputs what data have been added to database including row id for each table
"""

if (len(sys.argv)>3):
  configfile = sys.argv[3]
else:
  configfile = 'None'
pars = db.readconfig(configfile)

with db.create_tunnel(pars['TUNNELCMD']):

  with db.dbconnect(pars['CLINICALDBHOST'], pars['CLINICALDBPORT'], pars['STATSDB'], 
                        pars['CLINICALDBUSER'], pars['CLINICALDBPASSWD']) as dbc:

    ver = dbc.versioncheck(pars['STATSDB'], pars['DBVERSION'])

    if not ver == 'True':
      print "Wrong db " + pars['STATSDB'] + " v:" + pars['DBVERSION']
      exit(0) 
    else:
      print "Correct db " + pars['STATSDB'] + " v:" + pars['DBVERSION']

