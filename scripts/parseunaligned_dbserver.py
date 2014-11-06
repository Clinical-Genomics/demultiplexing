#!/usr/bin/python
#Script that connects to the MySQL database and parses data from an html table
#Import the mysql.connector library/module
#
#  from the bash script starting qc parsing to db
#  /home/clinical/SCRIPTS/parseunaligned_dbserver.py /home/clinical/DEMUX/${RUN}/ /home/clinical/RUNS/${RUN}/Data/Intensities/BaseCalls/SampleSheet.csv
#
import sys
import MySQLdb as mysql
from bs4 import BeautifulSoup
import time
import glob
import re
import socket

# this script is written for database version:
_MAJOR_ = 1
_MINOR_ = 0
_PATCH_ = 0

if (len(sys.argv)>1):
  basedir = sys.argv[1]
else:
  message = ("usage: "+sys.argv[0]+" <BASEDIRECTORYforUNALIGNED> <absolutepathtosamplesheetcsv>")
  exit(message)

params = {}
with open("/home/hiseq.clinical/.scilifelabrc", "r") as confs:
  for line in confs:
    if len(line) > 5 and not line[0] == "#":
      line = line.rstrip()
      pv = line.split(" ")
      params[pv[0]] = pv[1]

if not (basedir[-1:] == "/"):
  basedir = basedir+"/"

unaligned = (basedir+"Unaligned/Basecall_Stats*")
unaligned_stat_dir = glob.glob(unaligned)

# read in run parameters from Unaligned/support.txt
support = open(basedir+"Unaligned/support.txt")
support_lines = support.readlines()
support.close()


now = time.strftime('%Y-%m-%d %H:%M:%S')
cnx = mysql.connect(user=params['CLINICALDBUSER'], port=int(params['CLINICALDBPORT']), host=params['CLINICALDBHOST'], 
                    passwd=params['CLINICALDBPASSWD'], db='csdb_test')
cursor = cnx.cursor()

cursor.execute(""" SELECT major, minor, patch FROM version ORDER BY time DESC LIMIT 1 """)
row = cursor.fetchone()
while row is not None:
  print(row)
  major = row[0]
  minor = row[1]
  patch = row[2]
else:
  print "Incorrect DB, version not found."
  sys.exit("Incorrect DB, version not found.")

print "DB", major, minor, patch
print "sc", _MAJOR_, _MINOR_, _PATCH_

sys.exit("hejda")
#Determine the name of the basecall stats file
demultistats = (unaligned_stat_dir[0]+"/Demultiplex_Stats.htm")
soup = BeautifulSoup(open(demultistats))

h1fc = soup.find("h1")
fcentry = unicode(h1fc.string).encode('utf8')
fc = fcentry.replace("Flowcell: ","")
###print basedir
baseparts = basedir.split("_")
Flowcellpos = baseparts[len(baseparts)-1]
Flowcellpos = Flowcellpos.replace(fc+"/","") 
dirs = basedir.split("/")
runname = dirs[len(dirs)-2]
###print Flowcellpos
name_ = runname.split("_")
rundate = list(name_[0])
rundate = "20"+rundate[0]+rundate[1]+"-"+rundate[2]+rundate[3]+"-"+rundate[4]+rundate[5]

#print runname, rundate

#sys.exit(0)

print (basedir+"Unaligned/support.txt")
print (sys.argv[2])
exit
#print support_lines[5], len(support_lines)
system = ""
command = ""
idstring = ""
program = ""
samplesheet = (basedir + "Data/Intensities/BaseCalls/SampleSheet.csv")
for line in range(1, len(support_lines)):
  if re.match("^\$\_System", support_lines[line]):
    while not (re.match("};", support_lines[line])):
      system += support_lines[line]
      line += 1
  if re.match("^\$\_ID-string", support_lines[line]):
    idstring += support_lines[line]
  if re.match("^\$\_Program", support_lines[line]):
    program += support_lines[line]
  if re.match("^\$\_Command-line", support_lines[line]):
    while not (re.match("];", support_lines[line])):
      command += support_lines[line]
      line += 1
      if re.match("  '--sample-sheet',", support_lines[line]):
        samplesheet = support_lines[line+1]
        samplesheet = samplesheet.replace("  '","")
        samplesheet = samplesheet.replace("',\n","")

Idstring = idstring.replace("$_ID-string = '","")
Idstring = Idstring.replace("';","")
Idstring = Idstring.strip()
Program = program.replace("$_Program = '","")
Program = Program.replace("';","")
Program = Program.strip()
sysentries = system.splitlines()
Systempid = sysentries[1]
Systempid = Systempid.replace("  'PID' : '","")
Systempid = Systempid.replace("',","")
Systemos = sysentries[2]
Systemos = Systemos.replace("  'OS' : '","")
Systemos = Systemos.replace("',","")
Systemperlv = sysentries[3]
Systemperlv = Systemperlv.replace("  'PERL_VERSION' : '","")
Systemperlv = Systemperlv.replace("',","")
Systemperlexe = sysentries[4]
Systemperlexe = Systemperlexe.replace("  'PERL_EXECUTABLE' : '","")
Systemperlexe = Systemperlexe.replace("'","")
commandline = command.replace("$_Command-line = [\n","")

Samplesheet = open(samplesheet)
SampleSheet = ""
for line in Samplesheet.readlines():
  if re.match(",", line):
    SampleSheet += line
  line = line.strip()
  print line
Samplesheet.close()

print Idstring, Program, Systempid, Systemos, Systemperlv, Systemperlexe
print commandline, samplesheet
print SampleSheet
# ADD support params if not present in DB
cursor.execute(""" SELECT supportparams_id FROM supportparams WHERE document_path = %s """, (basedir+"Unaligned/support.txt", ))
if not cursor.fetchone():
  print "Support parameters not yet added"
  try:
    cursor.execute("""INSERT INTO `supportparams` (document_path, systempid, systemos, systemperlv, systemperlexe, idstring, program, commandline, sampleconfig_path, sampleconfig, time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """, (basedir+"Unaligned/support.txt", Systempid, Systemos, Systemperlv, Systemperlexe, Idstring, Program, commandline, samplesheet, SampleSheet, now, ))
  except mysql.IntegrityError, e: 
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("DB error")
# handle a specific error condition
  except mysql.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("Syntax error")
# handle a generic error condition
  except mysql.Warning, e:
    exit("MySQL warning")
# handle warnings, if the cursor you're using raises them
  cnx.commit()
  print "Support parameters from "+basedir+"Unaligned/support.txt"+" now added to DB with supportparams_id: "+str(cursor.lastrowid)
  supportparamsid = cursor.lastrowid
else:
  cursor.execute(""" SELECT supportparams_id FROM supportparams WHERE document_path = %s """, (basedir+"Unaligned/support.txt", ))
  supportparamsid = cursor.fetchone()[0]
  print "Support "+basedir+"Unaligned/support.txt"+" exists in DB with supportparams_id: "+str(supportparamsid)

#print system, idstring, program, command
# ADD datasource document if not present in DB
servername = socket.gethostname()
cursor.execute(""" SELECT datasource_id FROM datasource WHERE document_path = %s """, (demultistats, ))
if not cursor.fetchone():
  print "Data source not yet added"
  try:
    cursor.execute("""INSERT INTO `datasource` (document_path, runname, rundate, supportparams_id, server, time) VALUES (%s, %s, %s, %s, %s, %s) """, (demultistats, runname, rundate, supportparamsid, servername, now, ))
  except mysql.IntegrityError, e: 
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("DB error")
# handle a specific error condition
  except mysql.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("Syntax error")
# handle a generic error condition
  except mysql.Warning, e:
    exit("MySQL warning")
# handle warnings, if the cursor you're using raises them
  cnx.commit()
  print "Data source "+demultistats+" now added to DB with datasource_id: "+str(cursor.lastrowid)
  datasourceid = cursor.lastrowid
else:
  cursor.execute(""" SELECT datasource_id FROM datasource WHERE document_path = %s """, (demultistats, ))
  datasourceid = cursor.fetchone()[0]
  print "Data source "+demultistats+" exists in DB with datasource_id: "+str(datasourceid)

# ADD flowcell if not present in DB
cursor.execute(""" SELECT flowcell_id FROM flowcell WHERE flowcellname = %s """, (fc, ))
if not cursor.fetchone():
  print "Flowcell not yet added"
  try:
    cursor.execute("""INSERT INTO `flowcell` (datasource_id, flowcellname, flowcell_pos, time) VALUES (%s, %s, %s, %s) """, (str(datasourceid), fc, Flowcellpos, now, ))
  except mysql.IntegrityError, e: 
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("DB error")
# handle a specific error condition
  except mysql.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("Syntax error")
# handle a generic error condition
  except mysql.Warning, e:
    exit("MySQL warning")
# handle warnings, if the cursor you're using raises them
  cnx.commit()
  print "Flowcell "+fc+" now added to DB with flowcell_id: "+str(cursor.lastrowid)
  fcid = cursor.lastrowid
else:
  cursor.execute(""" SELECT flowcell_id FROM flowcell WHERE flowcellname = %s """, (fc, ))
  fcid = cursor.fetchone()[0]
  print "Flowcell "+fc+" exists in DB with flowcell_id: "+str(fcid)

# ADD project if not present in DB
projects = {}
tables = soup.findAll("table")
rows = tables[1].findAll('tr')
for row in rows:
  cols = row.findAll('td')
  project = unicode(cols[6].string).encode('utf8')
  
  cursor.execute(""" SELECT project_id, time FROM project WHERE projectname = %s """, (project, ))
  if not cursor.fetchone():
    print "Project not yet added"
    try:
      cursor.execute("""INSERT INTO `project` (projectname, time) VALUES (%s, %s) """, (project, now))
    except mysql.IntegrityError, e: 
      print "Error %d: %s" % (e.args[0],e.args[1])
      exit("DB error")
# handle a specific error condition
    except mysql.Error, e:
      print "Error %d: %s" % (e.args[0],e.args[1])
      exit("Syntax error")
# handle a generic error condition
    except mysql.Warning, e:
      exit("MySQL warning")
# handle warnings, if the cursor you're using raises them
    cnx.commit()
    print "Project "+project+" now added to DB with project_id: "+str(cursor.lastrowid)
    projects[project] = cursor.lastrowid
  else:
    cursor.execute(""" SELECT project_id FROM project WHERE projectname = %s """, (project, ))
    projid = cursor.fetchone()[0]
    print "Project "+project+" exists in DB with project_id: "+str(projid)
    projects[project] = projid

# ADD samples to DB
for var in projects:
  print var, projects[var]
samples = {}
for row in rows:
  cols = row.findAll('td')
  samplename = unicode(cols[1].string).encode('utf8')
  barcode = unicode(cols[3].string).encode('utf8')
  project = unicode(cols[6].string).encode('utf8')
  cursor.execute(""" SELECT sample.sample_id FROM sample, unaligned, flowcell WHERE samplename = %s AND barcode = %s AND sample.sample_id = unaligned.sample_id AND unaligned.flowcell_id = flowcell.flowcell_id AND flowcell.datasource_id = %s """, (samplename, barcode, str(datasourceid), ))
  if not cursor.fetchone():
    print "Sample not yet added"
    try:
      cursor.execute("""INSERT INTO `sample` (samplename, project_id, barcode, time) VALUES (%s, %s, %s, %s) """, (samplename, projects[project], barcode, now, ))
    except mysql.IntegrityError, e: 
      print "Error %d: %s" % (e.args[0],e.args[1])
      exit("DB error")
# handle a specific error condition
    except mysql.Error, e:
      print "Error %d: %s" % (e.args[0],e.args[1])
      exit("Syntax error")
# handle a generic error condition
    except mysql.Warning, e:
      exit("MySQL warning")
# handle warnings, if the cursor you're using raises them
    cnx.commit()
    print "Sample "+samplename+" now added to DB with sample_id: "+str(cursor.lastrowid)
    samples[samplename] = cursor.lastrowid
  else:
    cursor.execute(""" SELECT sample.sample_id FROM sample, unaligned, flowcell WHERE samplename = %s AND barcode = %s AND sample.sample_id = unaligned.sample_id AND unaligned.flowcell_id = flowcell.flowcell_id AND flowcell.datasource_id = %s """, (samplename, barcode, str(datasourceid), ))
    sampleid = cursor.fetchone()[0]
    print "Sample "+samplename+" exists in DB with sample_id: "+str(sampleid)
    samples[samplename] = sampleid

# ADD Demultiplexing data
for row in rows:
  cols = row.findAll('td')
  lane = unicode(cols[0].string).encode('utf8')
  samplename = unicode(cols[1].string).encode('utf8')
  barcode = unicode(cols[3].string).encode('utf8')
  project = unicode(cols[6].string).encode('utf8')
  yield_mb = unicode(cols[7].string).encode('utf8')
  yield_mb = yield_mb.replace(",","")
  passed_filter_pct = unicode(cols[8].string).encode('utf8')
  Readcounts = unicode(cols[9].string).encode('utf8')
  Readcounts = Readcounts.replace(",","")
  raw_clusters_per_lane_pct = unicode(cols[10].string).encode('utf8')
  perfect_indexreads_pct = unicode(cols[11].string).encode('utf8')
  q30_bases_pct = unicode(cols[13].string).encode('utf8')
  mean_quality_score = unicode(cols[14].string).encode('utf8')

  cursor.execute(""" SELECT unaligned_id FROM unaligned WHERE sample_id = %s AND lane = %s """, (str(samples[samplename]), lane, ))
  if not cursor.fetchone():
    print "UnalignedStats not yet added"
    try:
      cursor.execute("""INSERT INTO `unaligned` (sample_id, flowcell_id, lane, yield_mb, passed_filter_pct, readcounts, raw_clusters_per_lane_pct, perfect_indexreads_pct, q30_bases_pct, mean_quality_score, time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """, (samples[samplename], str(fcid), lane, yield_mb, passed_filter_pct, Readcounts, raw_clusters_per_lane_pct, perfect_indexreads_pct, q30_bases_pct, mean_quality_score, now, ))
    except mysql.IntegrityError, e: 
      print "Error %d: %s" % (e.args[0],e.args[1])
      exit("DB error")
# handle a specific error condition
    except mysql.Error, e:
      print "Error %d: %s" % (e.args[0],e.args[1])
      exit("Syntax error")
# handle a generic error condition
    except mysql.Warning, e:
      exit("MySQL warning")
# handle warnings, if the cursor you're using raises them
    cnx.commit()
    print "Unaligned stats for sample "+samplename+" now added to DB with unaligned_id: "+str(cursor.lastrowid)
  else:
    cursor.execute(""" SELECT unaligned_id FROM unaligned WHERE sample_id = %s AND lane = %s """, (str(samples[samplename]), lane, ))
    unalignedid = cursor.fetchone()[0]
    print "Unaligned stats for sample "+samplename+" exists in DB with unaligned_id: "+str(unalignedid)

cnx.commit()

#Closes the cursor
cursor.close()
#Closes the connection to the database
cnx.close()


