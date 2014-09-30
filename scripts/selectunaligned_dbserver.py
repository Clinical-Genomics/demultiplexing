#!/usr/bin/python
#Script that connects to the MySQL database and parses data from an html table
#Import the mysql.connector library/module
import sys
import MySQLdb as mysql
from bs4 import BeautifulSoup
import time
import glob
import re

params = {}
with open("/home/hiseq.clinical/.scilifelabrc", "r") as confs:
  for line in confs:
    if len(line) > 5 and not line[0] == "#":
      line = line.rstrip()
      pv = line.split(" ")
      params[pv[0]] = pv[1]

now = time.strftime('%Y-%m-%d %H:%M:%S')
cnx = mysql.connect(user=params['CLINICALDBUSER'], port=int(params['CLINICALDBPORT']), host=params['CLINICALDBHOST'], passwd=params['CLINICALDBPASSWD'], db='clinstatsdb')
cursor = cnx.cursor()

# SELECT stats
proje = sys.argv[1]
flowc = sys.argv[2]
cursor.execute(""" SELECT sample.samplename, flowcell.flowcellname, GROUP_CONCAT(unaligned.lane ORDER BY unaligned.lane), GROUP_CONCAT(unaligned.readcounts ORDER BY unaligned.lane), SUM(unaligned.readcounts), GROUP_CONCAT(unaligned.yield_mb ORDER BY unaligned.lane), SUM(unaligned.yield_mb), GROUP_CONCAT(TRUNCATE(q30_bases_pct,2) ORDER BY unaligned.lane), GROUP_CONCAT(TRUNCATE(mean_quality_score,2) ORDER BY unaligned.lane)
FROM sample, flowcell, unaligned, project
WHERE sample.sample_id     = unaligned.sample_id
AND   flowcell.flowcell_id = unaligned.flowcell_id
AND   sample.project_id    = project.project_id 
AND   project.projectname    =  %s
AND   flowcell.flowcellname = %s
GROUP BY samplename, flowcell.flowcell_id
ORDER BY lane, sample.samplename, flowcellname """, (proje, flowc, ))
data = cursor.fetchall()
print "sample\tFlowcell\tLanes\treadcounts/lane\tsum_readcounts\tyieldMB/lane\tsum_yield\t%Q30\tMeanQscore"
for row in data:
  print row[0]+"\t"+row[1]+"\t"+row[2]+"\t"+row[3]+"\t"+str(row[4])+"\t"+str(row[5])+"\t"+str(row[6])+"\t"+str(row[7])+"\t"+str(row[8])



cursor.close()
cnx.close()
