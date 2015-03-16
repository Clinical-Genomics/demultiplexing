#!/usr/bin/python
#
import sys
import datetime
import os
from access import db

print sys.argv[0], sys.argv[1], sys.argv[2], sys.argv[3]

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

    proje = sys.argv[1]
    flowc = sys.argv[2]
    query = (""" SELECT sample.samplename, flowcell.flowcellname, GROUP_CONCAT(unaligned.lane ORDER BY unaligned.lane), 
    GROUP_CONCAT(unaligned.readcounts ORDER BY unaligned.lane), SUM(unaligned.readcounts), 
    GROUP_CONCAT(unaligned.yield_mb ORDER BY unaligned.lane), SUM(unaligned.yield_mb), 
    GROUP_CONCAT(TRUNCATE(q30_bases_pct,2) ORDER BY unaligned.lane), 
    GROUP_CONCAT(TRUNCATE(mean_quality_score,2) ORDER BY unaligned.lane) 
    FROM sample, flowcell, unaligned, project, demux WHERE sample.sample_id = unaligned.sample_id 
    AND flowcell.flowcell_id = demux.flowcell_id AND unaligned.demux_id = demux.demux_id 
    AND sample.project_id = project.project_id AND project.projectname = %s AND flowcell.flowcellname = %s 
    GROUP BY samplename, flowcell.flowcell_id ORDER BY lane, sample.samplename, flowcellname; """, (proje, flowc, ))
    hits = dbc.generalquery(query)
    print "sample\tFlowcell\tLanes\treadcounts/lane\tsum_readcounts\tyieldMB/lane\tsum_yield\t%Q30\tMeanQscore"
    for hit in hits:
      print (hit[0] + "\t" + hit[1] + "\t" + hit[2] + "\t" + hit[3] + "\t" + str(hit[4]) + "\t" + str(hit[5]) + "\t" + 
             str(hit[6]) + "\t" + str(hit[7]) + "\t" + str(hit[8]))
