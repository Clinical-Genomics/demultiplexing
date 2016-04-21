#!/usr/bin/python
#
import sys
from access import db

"""Reads stats from db.
  usage: selectdemux.py <project> <flowcell> <config_file:optional>"
Args:
  project (str): name of project in database
  flowcell (str): name of flowcell in database
Returns:
  str: statistics for each sample in project on flowcell [stored in database]
"""

if (len(sys.argv)>3):
  configfile = sys.argv[3]
else:
  configfile = 'None'
pars = db.readconfig(configfile)

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
  query = """ SELECT sample.samplename AS smp, flowcell.flowcellname AS flc, 
  GROUP_CONCAT(unaligned.lane ORDER BY unaligned.lane) AS lanes, 
  GROUP_CONCAT(unaligned.readcounts ORDER BY unaligned.lane) AS rds, SUM(unaligned.readcounts) AS readsum, 
  GROUP_CONCAT(unaligned.yield_mb ORDER BY unaligned.lane) AS yield, SUM(unaligned.yield_mb) AS yieldsum, 
  GROUP_CONCAT(TRUNCATE(q30_bases_pct,2) ORDER BY unaligned.lane) AS q30, 
  GROUP_CONCAT(TRUNCATE(mean_quality_score,2) ORDER BY unaligned.lane) AS meanq
  FROM sample, flowcell, unaligned, project, demux WHERE sample.sample_id = unaligned.sample_id 
  AND flowcell.flowcell_id = demux.flowcell_id AND unaligned.demux_id = demux.demux_id 
  AND sample.project_id = project.project_id AND project.projectname = '""" + proje + """' 
  AND flowcell.flowcellname = '""" + flowc + """' GROUP BY samplename, flowcell.flowcell_id 
  ORDER BY lane, sample.samplename, flowcellname """
  hits = dbc.generalquery(query)
  print "sample\tFlowcell\tLanes\treadcounts/lane\tsum_readcounts\tyieldMB/lane\tsum_yield\t%Q30\tMeanQscore"
  for hit in hits:
    print hit['smp'] + "\t" + hit['flc'] + "\t" + hit['lanes'] + "\t" + hit['rds'] + "\t" + str(hit['readsum']) + "\t" + str(hit['yield']) + "\t" + str(hit['yieldsum']) + "\t" + str(hit['q30']) + "\t" + str(hit['meanq'])
