#!/usr/bin/python
#
import sys
import datetime
import os
from access import db

if (len(sys.argv)>1):
  db.configfile = sys.argv[1]
else:
  configfile = 'None'
pars = db.readconfig(configfile)

with db.create_tunnel(pars['TUNNELCMD']):

  with db.dbconnect(pars['CLINICALDBHOST'], pars['CLINICALDBPORT'], pars['STATSDB'], 
                        pars['CLINICALDBUSER'], pars['CLINICALDBPASSWD']) as dbc:

    ver = dbc.versioncheck(pars['STATSDB'], pars['DBVERSION'])

    if not ver == 'True':
      print "Wrong db " + pars['STATSDB'] + " v:" + ver
      exit(0) 
    else:
      print "Correct db " + pars['STATSDB'] + " v:" + ver
