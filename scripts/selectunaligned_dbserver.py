#!/usr/bin/python
#Script that connects to the MySQL database and parses data from an html table
#Import the mysql.connector library/module
import sys
import MySQLdb as mysql
from bs4 import BeautifulSoup
import time
import glob
import re
import os

# this script is written for database version:
_MAJOR_ = 1
_MINOR_ = 0
_PATCH_ = 0

if (len(sys.argv)>1):
  basedir = sys.argv[1]
else:
  message = ("usage: "+sys.argv[0]+" <project> <flowcell> <config_file:optional>")
  sys.exit(message)

configfile = "/home/hiseq.clinical/.scilifelabrc"
if (len(sys.argv)>3):
  if os.path.isfile(sys.argv[3]):
    configfile = sys.argv[3]
    
params = {}
with open(configfile, "r") as confs:
  for line in confs:
    if len(line) > 5 and not line[0] == "#":
      line = line.rstrip()
      pv = line.split(" ")
      params[pv[0]] = pv[1]

# config file test
#sys.exit(configfile+ params['STATSDB'])


now = time.strftime('%Y-%m-%d %H:%M:%S')
cnx = mysql.connect(user=params['CLINICALDBUSER'], port=int(params['CLINICALDBPORT']), host=params['CLINICALDBHOST'], 
                    passwd=params['CLINICALDBPASSWD'], db=params['STATSDB'])
cursor = cnx.cursor()

cursor.execute(""" SELECT major, minor, patch FROM version ORDER BY time DESC LIMIT 1 """)
row = cursor.fetchone()
if row is not None:
  major = row[0]
  minor = row[1]
  patch = row[2]
else:
  sys.exit("Incorrect DB, version not found.")
if (major == _MAJOR_ and minor == _MINOR_ and patch == _PATCH_):
  print "Correct database "+str(_MAJOR_)+"."+str(_MINOR_)+"."+str(_PATCH_)
else:
  exit ("Incorrect DB version. This script is made for "+str(_MAJOR_)+"."+str(_MINOR_)+"."+str(_PATCH_)+" not for "+str(major)+"."+str(minor)+"."+str(patch))

# SELECT stats
proje = sys.argv[1]
flowc = sys.argv[2]
cursor.execute(""" SELECT sample.samplename, flowcell.flowcellname, GROUP_CONCAT(unaligned.lane ORDER BY unaligned.lane), GROUP_CONCAT(unaligned.readcounts ORDER BY unaligned.lane), SUM(unaligned.readcounts), GROUP_CONCAT(unaligned.yield_mb ORDER BY unaligned.lane), SUM(unaligned.yield_mb), GROUP_CONCAT(TRUNCATE(q30_bases_pct,2) ORDER BY unaligned.lane), GROUP_CONCAT(TRUNCATE(mean_quality_score,2) ORDER BY unaligned.lane)
FROM sample, flowcell, unaligned, project
WHERE sample.sample_id     = unaligned.sample_id
AND   flowcell.flowcell_id = unaligned.flowcell_id
AND   sample.project_id    = project.project_id 
AND   project.projectname   =  %s
AND   flowcell.flowcellname = %s
GROUP BY samplename, flowcell.flowcell_id
ORDER BY lane, sample.samplename, flowcellname """, (proje, flowc, ))
data = cursor.fetchall()
print "sample\tFlowcell\tLanes\treadcounts/lane\tsum_readcounts\tyieldMB/lane\tsum_yield\t%Q30\tMeanQscore"
for row in data:
  print row[0]+"\t"+row[1]+"\t"+row[2]+"\t"+row[3]+"\t"+str(row[4])+"\t"+str(row[5])+"\t"+str(row[6])+"\t"+str(row[7])+"\t"+str(row[8])



cursor.close()
cnx.close()
