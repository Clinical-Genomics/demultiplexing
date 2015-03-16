#!/usr/bin/python
#
import sys
import datetime
import os
from access import *

if (len(sys.argv)>1):
  configfile = sys.argv[1]
else:
  configfile = 'None'
pars = readconfig(configfile)

if not os.path.isdir(pars['BACKUPCOPYFOLDER']):
  sys.exit("No directory " + pars['BACKUPCOPYFOLDER'])

with create_tunnel(pars['TUNNELCMD']):

  with dbconnect(pars['CLINICALDBHOST'], pars['CLINICALDBPORT'], pars['STATSDB'], 
                        pars['CLINICALDBUSER'], pars['CLINICALDBPASSWD']) as dbc:

    ver = dbc.versioncheck(pars['STATSDB'], pars['DBVERSION'])

    if not ver == 'True':
      print "Wrong db " + pars['STATSDB'] + " v:" + ver
      exit(0) 
    else:
      print "Correct db " + pars['STATSDB'] + " v:" + ver
