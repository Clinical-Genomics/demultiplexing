#!/usr/bin/python
#
import sys
import os
import glob
import time
import re
import socket
from bs4 import BeautifulSoup
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
    demux_stat_dir = glob.glob(demux)[0]
    if not os.path.isdir(demux_stat_dir): 
      exit("Bad statistics dir")
    if not (demux_stat_dir[-1:] == "/"):
      demux_stat_dir = demux_stat_dir + "/"

    if not os.path.isfile(basedir + unaligned + "support.txt"):
      exit ("Bad support.txt")
    support = open(basedir + unaligned + "support.txt")
    support_lines = support.readlines()
    support.close()

    demultistats = (demux_stat_dir + "Demultiplex_Stats.htm")
    if not os.path.isfile(demultistats):
      exit("Bad demux stats file")
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
    machine = name_[1]
    print runname, rundate, machine

    system = ""
    command = ""
    idstring = ""
    program = ""
#print samplesheet
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
    SampleSheet = Samplesheet.read()
#    for line in Samplesheet.readlines():
#      print "LINE", line
#      if re.match(",", line):
#        SampleSheet += line
#      line = line.strip()
#      print line
    Samplesheet.close()

    print Idstring, Program, Systempid, Systemos, Systemperlv, Systemperlexe
    print commandline, samplesheet
    print SampleSheet
    
    clas = commandline.split('\n')
    isbm = False
    for cla in clas:
      if isbm:
        bmask = cla.split("'")[1]
        isbm = False
      if cla == "  '--use-bases-mask',":
        isbm = True
    if not bmask:
      exit("Bad basemask")
    else:
      print bmask

    now = time.strftime('%Y-%m-%d %H:%M:%S')

    """ Set up data for supportparams table """

    getsupportquery = (""" SELECT supportparams_id FROM supportparams WHERE document_path = '""" + basedir + unaligned + 
                      """support.txt' """)
    print getsupportquery
    indbsupport = dbc.generalquery(getsupportquery)
    if not indbsupport:
      print "Support parameters not yet added"
      insertdict = { 'document_path': basedir + unaligned + 'support.txt', 'systempid': Systempid, 
                     'systemos': Systemos, 'systemperlv': Systemperlv, 'systemperlexe': Systemperlexe,
                     'idstring': Idstring, 'program': Program, 'commandline': commandline, 
                     'sampleconfig_path': samplesheet, 'sampleconfig': SampleSheet, 'time': now }
      supportparamsid = dbc.sqlinsert('supportparams', insertdict)
    else:
      supportparamsid = indbsupport[0]['supportparams_id']
    print "Support " + basedir + unaligned + 'support.txt' + " exists in DB with supportparams_id: " + str(supportparamsid)

    """ Set up data for table datasource """
    
    servername = socket.gethostname()
    getdatasquery = """ SELECT datasource_id FROM datasource WHERE document_path = '""" + demultistats + """' """
    print getdatasquery
    indbdatas = dbc.generalquery(getdatasquery)
    if not indbdatas:
      print "Data source not yet added"
      insertdict = { 'document_path': demultistats, 'runname': runname, 'rundate': rundate, 'machine': machine, 
                     'supportparams_id': supportparamsid, 'server': servername, 'time': now }
      datasourceid = dbc.sqlinsert('datasource', insertdict)
    else:
      datasourceid = indbdatas[0]['datasource_id']
    print "Datasource " + demultistats + " exists in DB with datasource_id: "+str(datasourceid)

    """ Set up data for table flowcell """

    getflowcellquery = """ SELECT flowcell_id FROM flowcell WHERE flowcellname = '""" + fc + """' """
    indbfc = dbc.generalquery(getflowcellquery)
    if not indbfc:
      print "Data source not yet added"
      insertdict = { 'flowcellname': fc, 'flowcell_pos': Flowcellpos, 'time': now }
      flowcellid = dbc.sqlinsert('flowcell', insertdict)
    else:
      flowcellid = indbfc[0]['flowcell_id']
    print "Flowcell " + fc + " exists in DB with flowcell_id: " + str(flowcellid)

    """ Set up data for table demux """
    
    getdemuxquery = """ SELECT demux_id FROM demux WHERE flowcell_id = '""" + str(flowcellid) + """' 
                        AND datasource_id = '""" + str(datasourceid) + """' AND basemask = '""" + bmask + """' """
    indbdemux = dbc.generalquery(getdemuxquery)
    if not indbdemux:
      print "Demux not yet added"
      insertdict = { 'flowcell_id': flowcellid, 'datasource_id': datasourceid, 'basemask': bmask, 'time': now }
      demuxid = dbc.sqlinsert('demux', insertdict)
    else:
      demuxid = indbdemux[0]['demux_id']
    print "Demux " + bmask + " from Flowcell: " + fc + " exists in DB with demux_id: " + str(demuxid)


    print now
