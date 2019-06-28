#!/usr/local/bin/python

#-------------------------------------------------------------------------------
#
# parse_riverside_data.py
#
# Copyright 2008 Idaho Coalition of Home Educators (ICHE). All rights reserved.
# Written by Bruce Dickey -- bruce@thedickeys.net.
#
# History
#    2008-Jun-20 BD Added checking of test data file, with logging and exceptions.
#                   Added logging of Python version.
#                   Added logging of MySQL version info.
#                   Added catching of unknown exceptions.
#    2008-Jun-18 BD Added shebang on line 1.
#                   Added ClearStatusFile() to clear the status file at the 
#                     beginning of each run.
#                   Added a check of cursor.messages for error messages after
#                     each cursor method call.
#                   Added catching of MySQLdb.Error exceptions and writing of
#                     them to the parse_riverside_data_status.txt file.
#                   Added cursor.close(), db.commit(), and db.close() at the end
#                     of __main__.
#    2008-Jun-03 BD Created
#
#-------------------------------------------------------------------------------

# Python imports
import sys
import os
import os.path
import platform

# Third-party imports
import MySQLdb   # Python interface to MySQL
from MySQLdb.release import version_info


#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------

# Riverside data CSV columns; 0-based
TEST_TYPE     =  1    # 'ITBS' or 'ITED'
STATE         =  2
BUILDING_NAME =  7    # Contains both ICHE region number and region name
CLASS_NAME    =  9    # ICHE 'Campus'. Is compass directions.
#                       ICHE uses 'N' 'S' 'E' 'W' instead of spelled out as Riverside does.
GRADE         = 11   
DATE_TESTED   = 12
LAST_NAME     = 13
FIRST_NAME    = 14
GENDER        = 15
BIRTHDATE     = 16
STUDENT_ID    = 17
LEVEL         = 19
RAW_SCORES    = 34
STD_SCORES    = 35
GRD_SCORES    = 36
NPR_SCORES    = 38
NCE_SCORES    = 40
NST_SCORES    = 41

global bConsoleDebug
bConsoleDebug = False

#-------------------------------------------------------------------------------
# Functions
#-------------------------------------------------------------------------------

def ClearLogFile():
	f = file('parse_riverside_data_log.txt', 'w')
	f.close()
#


def Log(inStr):
	if bConsoleDebug:
		print inStr   # Send to stdout too

	f = file('parse_riverside_data_log.txt', 'a')
	f.write(inStr + '\n')
	f.close()
#


def ClearStatusFile():
	f = file('parse_riverside_data_status.txt', 'w')
	f.close()
#


def WriteStatusFile(inStr):
	f = file('parse_riverside_data_status.txt', 'a')
	f.write(inStr + '\n')
	f.close()
#


def SplitFixedWidth(inStr, numDataItems, dataWidth):
	data = []
	i = 0
	j = dataWidth

	while j < ( (numDataItems + 1) * dataWidth):
		data.append( inStr[i:j] )
		i += dataWidth
		j += dataWidth
	#

	return data
#


def WriteStudentTable(cursor, stuData, tableName):
	# Check for 'tableName' table. If it doesn't exist, create it.
	cursor.execute("show tables;")
	tmpAllTables = cursor.fetchall()	    # Returns a list of one-element lists (actually Python tuples which are immutable lists).
	allTables = [ x[0] for x in tmpAllTables ]  # Flattens the 2-dim list to one-dim. The data we want is in the first element of each sublist.  
	# This Python construct is called a "list comprehension".

	Log('After WriteStudentTable(), show tables')

	if not tableName in allTables:
		# Create the table
		cmd = ''.join(["CREATE TABLE `", tableName, "` (\n",
							" `testing_history_id` int(10) unsigned   default NULL,\n",
							" `score_id`           int(10) unsigned   AUTO_INCREMENT,\n",
							" `member_id`          int(10) unsigned   default NULL,\n",
							" `student_id`         int(10) unsigned   default NULL,\n",
							" `l_name`             varchar(30)        NOT NULL,\n",
							" `f_name`             varchar(30)        NOT NULL,\n",
							" `gender`             enum('m','f')      NOT NULL,\n",
							" `dob`                date               NOT NULL,\n",
							" `grade`              int(2) unsigned    NOT NULL  default '0', \n",
							" `level`              int(2) unsigned    NOT NULL  default '0', \n",
							" `date_tested`        date               NOT NULL,\n",
							" `test_type`          char(4)            NOT NULL,\n",
							" `region_name`        varchar(30)        NOT NULL,\n",
							" `region_num`         int(2)  unsigned   NOT NULL,\n",
							" `campus`             enum('N','S','E','W')  NOT NULL,\n",
							" `state`              varchar(30)        default NULL,\n",
                            " `nat_id`              varchar(11)        default NULL,\n",
							" PRIMARY KEY (`score_id`)\n)\n",
							" ENGINE=MyISAM  DEFAULT CHARSET=latin1 PACK_KEYS=0 AUTO_INCREMENT=2"])
		#print cmd   # DEBUG
		cursor.execute(cmd)

		Log('After WriteStudentTable(), create table')

		if len(cursor.connection.messages) > 0:
			msgs = '\n'.join(['Connection Error(s) executing CREATE TABLE for table ' + tableName] + cursor.messages)   # DEBUG
			raise Exception(msgs)
		#

		if len(cursor.messages) > 0:
			msgs = '\n'.join(['Cursor Error(s) executing CREATE TABLE for table ' + tableName] + cursor.messages)   # DEBUG
			raise Exception(msgs)
		#

		Log('After WriteStudentTable(), create table messages check')

	# End if not table

	# Add data to the table
	tmpData = [stuData.lastName, stuData.firstName, stuData.gender, stuData.dob,
				  stuData.grade, stuData.level, stuData.dateTested, stuData.testType,
				  stuData.regionNum, stuData.regionName, stuData.campus, stuData.state]

	cmd = ''.join(["INSERT INTO ", tableName,
						" ( l_name, f_name, gender, dob, grade, level, date_tested, \n",
						"test_type, region_num, region_name, campus, state ) \n",
						" VALUES (", ','.join( ["'" + x + "'" for x in tmpData]), ")" ])
	#print cmd   # DEBUG
	cursor.execute(cmd)

	Log('After WriteStudentTable(), insert')

	if len(cursor.connection.messages) > 0:
		msgs = '\n'.join(['Connection Error(s) executing INSERT for table ' + tableName] + cursor.messages)   # DEBUG
		raise Exception(msgs)
	#

	if len(cursor.messages) > 0:
		msgs = '\n'.join(['Cursor Error(s) executing INSERT for table ' + tableName] + cursor.messages)   # DEBUG
		raise Exception(msgs)
	#

	Log('After WriteStudentTable(), insert messages check')

# End WriteStudentTable()


def OLDWriteScoreTable(cursor, scoreData, tableName, dataType):
	# Check for 'tableName' table. If it doesn't exist, create it.
	cursor.execute("show tables;")
	tmpAllTables = cursor.fetchall()            # Returns a list of one-element lists (actually Python tuples).
	allTables = [ x[0] for x in tmpAllTables ]  # Flattens the 2-dim list to one-dim. The data we want is in the first element of each sublist.

	Log('After WriteScoreTable(%s), show tables' % tableName)

	if not tableName in allTables:
		# Create the table
		cmd = ''.join(["CREATE TABLE `", tableName, "` (\n",
							" `score_id`        int(10) unsigned NOT NULL,\n",
							" `vocabulary`      ", dataType, " default 0,\n",
							" `reading_comp`    ", dataType, " default 0,\n",
							" `reading_total`   ", dataType, " default 0,\n",
							" `filler_4`        ", dataType, " default 0,\n",
							" `filler_5`        ", dataType, " default 0,\n",
							" `spelling`        ", dataType, " default 0,\n",
							" `capital`         ", dataType, " default 0,\n",
							" `punct`           ", dataType, " default 0,\n",
							" `usage_expr`      ", dataType, " default 0,\n",
							" `lang_total`      ", dataType, " default 0,\n",
							" `concepts_est`    ", dataType, " default 0,\n",
							" `itbs_prov_solv`  ", dataType, " default 0,\n",
							" `ited_prob_solv`  ", dataType, " default 0,\n",
							" `computation`     ", dataType, " default 0,\n",
							" `math_total`      ", dataType, " default 0,\n",
							" `filler_16`       ", dataType, " default 0,\n",
							" `core_total`      ", dataType, " default 0,\n",
							" `social_studies`  ", dataType, " default 0,\n",
							" `science`         ", dataType, " default 0,\n",
							" `maps_diag`       ", dataType, " default 0,\n",
							" `ref_matrl`       ", dataType, " default 0,\n",
							" `info_src`        ", dataType, " default 0,\n",
							" `filler_23`       ", dataType, " default 0,\n",
							" `composite`       ", dataType, " default 0,\n",
							" `filler_25`       ", dataType, " default 0,\n",
							" `filler_26`       ", dataType, " default 0,\n",
							" `filler_27`       ", dataType, " default 0,\n",
							" `filler_28`       ", dataType, " default 0,\n",
							" `filler_29`       ", dataType, " default 0,\n",
							" `filler_30`       ", dataType, " default 0,\n",
							" PRIMARY KEY  (`score_id`)\n)\n",
							" ENGINE=MyISAM  DEFAULT CHARSET=latin1 PACK_KEYS=0"])
		#print cmd   # DEBUG
		cursor.execute(cmd)


		Log('After WriteScoreTable(%s), create table' % tableName)

		if len(cursor.connection.messages) > 0:
			msgs = '\n'.join(['Connection Error(s) executing CREATE TABLE for table ' + tableName] + cursor.messages)   # DEBUG
			raise Exception(msgs)
		#

		if len(cursor.messages) > 0:
			msgs = '\n'.join(['Cursor Error(s) executing CREATE TABLE for table ' + tableName] + cursor.messages)   # DEBUG
			raise Exception(msgs)
		#

		Log('After WriteScoreTable(%s), create table messsages check' % tableName)

	# End if not table


	# Get the latest score_id to link this table to the score_student_data table
	cursor.execute('select max(score_id) from score_student_data')
	tmpScoreId = cursor.fetchall()
	score_id = tmpScoreId[0][0]

	# Change blank scores to zeros for db int data type
	#print 'scoreData =', str(scoreData)   # DEBUG
	for i in range ( len(scoreData) ):
		if scoreData[i] in ['    ', '   ', '  ', ' ']: scoreData[i] = '0'
	#

	# Add data to the table
	tmpData = ''.join(["'", str(score_id), "',", ', '.join( ["'" + x + "'" for x in scoreData] )])
	#print 'tmpData =', tmpData   # DEBUG

	cmd = ''.join(["INSERT INTO ", tableName,
						" ( score_id, vocabulary, reading_comp, reading_total, word_analysis__empty, listening__empty, \n",
						"spelling, capitalization__empty, punct_reading__empty, usage_expr__empty, lang_total__revise_writ, concepts_est__empty, \n",
						"probs_data_interp, math_total_minus_comp__concepts_probs, computation, math_total_plus_comp, core_total_minus_comp, core_total_plus_comp, \n",
						"social_studies, science, maps_diagrams__empty, ref_material__empty, srcs_tot__info_srcs, composite_minus_comp, composite_plus_comp, \n",
						"filler_25, filler_26, read_profile_tot_plus__empty, read_profile_tot_minus__empty, filler_29, filler_30 ) \n",
						" VALUES (", tmpData, ")"])
	#print cmd   # DEBUG
	cursor.execute(cmd)

	Log('After WriteScoreTable(%s), insert' % tableName)

	if len(cursor.connection.messages) > 0:
		msgs = '\n'.join(['Connection Error(s) executing INSERT for table ' + tableName] + cursor.messages)   # DEBUG
		raise Exception(msgs)
	#

	if len(cursor.messages) > 0:
		msgs = '\n'.join(['Cursor Error(s) executing INSERT for table ' + tableName] + cursor.messages)   # DEBUG
		raise Exception(msgs)
	#

	Log('After WriteScoreTable(%s), insert messages check' % tableName)

# End OLDWriteScoreTable()


def WriteItbsScoreTable(cursor, scoreData, tableName, dataType):
	# Check for 'tableName' table. If it doesn't exist, create it.
	cursor.execute("show tables;")
	tmpAllTables = cursor.fetchall()            # Returns a list of one-element lists (actually Python tuples).
	allTables = [ x[0] for x in tmpAllTables ]  # Flattens the 2-dim list to one-dim. The data we want is in the first element of each sublist.

	Log('After WriteItbsScoreTable(%s), show tables' % tableName)

	if not tableName in allTables:
		# Create the table   ('|' to separate ITBS/ITED where there are differences)
		cmd = ''.join(["CREATE TABLE `", tableName, "` (\n",
							" `score_id`          int(10) unsigned NOT NULL,\n",
							" `vocabulary`        ", dataType, " default 0,\n",
							" `reading_compreh`   ", dataType, " default 0,\n",
							" `reading_total`     ", dataType, " default 0,\n",
							" `word_analysis`     ", dataType, " default 0,\n",
							" `listening`         ", dataType, " default 0,\n",
							" `spelling`          ", dataType, " default 0,\n",
							" `capitalization`    ", dataType, " default 0,\n",
							" `punct_read_word`   ", dataType, " default 0,\n",
							" `usage_expression`  ", dataType, " default 0,\n",
							" `language_total`    ", dataType, " default 0,\n",
							" `concepts_est`      ", dataType, " default 0,\n",
							" `prob_data_interp`  ", dataType, " default 0,\n",
							" `mathT_mComput`     ", dataType, " default 0,\n",
							" `computation`       ", dataType, " default 0,\n",
							" `mathT_pComput`     ", dataType, " default 0,\n",
							" `coreT_mComput`     ", dataType, " default 0,\n",
							" `coreT_pComput`     ", dataType, " default 0,\n",
							" `social_studies`    ", dataType, " default 0,\n",
							" `science`           ", dataType, " default 0,\n",
							" `maps_diagrams`     ", dataType, " default 0,\n",
							" `ref_mtrls`         ", dataType, " default 0,\n",
							" `sources_total`     ", dataType, " default 0,\n",
							" `composite_mComput` ", dataType, " default 0,\n",
							" `composite_pComput` ", dataType, " default 0,\n",
							" `filler_25`         ", dataType, " default 0,\n",
							" `filler_26`         ", dataType, " default 0,\n",
							" `rdProfileT_pWords` ", dataType, " default 0,\n",
							" `rdProfileT_mWords` ", dataType, " default 0,\n",
							" `filler_29`         ", dataType, " default 0,\n",
							" `filler_30`         ", dataType, " default 0,\n",
							" PRIMARY KEY  (`score_id`)\n)\n",
							" ENGINE=MyISAM  DEFAULT CHARSET=latin1 PACK_KEYS=0"])
		#print cmd   # DEBUG
		cursor.execute(cmd)

		Log('After WriteItbsScoreTable(%s), create table' % tableName)

		if len(cursor.connection.messages) > 0:
			msgs = '\n'.join(['Connection Error(s) executing CREATE TABLE for table ' + tableName] + cursor.messages)   # DEBUG
			raise Exception(msgs)
		#

		if len(cursor.messages) > 0:
			msgs = '\n'.join(['Cursor Error(s) executing CREATE TABLE for table ' + tableName] + cursor.messages)   # DEBUG
			raise Exception(msgs)
		#

		Log('After WriteItbsScoreTable(%s), create table messsages check' % tableName)

	# End if not table


	# Get the latest score_id to link this table to the score_student_data table
	cursor.execute('select max(score_id) from score_student_data')
	tmpScoreId = cursor.fetchall()
	score_id = tmpScoreId[0][0]

	# Change blank scores to zeros for db int data type
	#print 'scoreData =', str(scoreData)   # DEBUG
	for i in range ( len(scoreData) ):
		if scoreData[i] in ['    ', '   ', '  ', ' ']: scoreData[i] = '0'
	#

	# Add data to the table
	tmpData = ''.join(["'", str(score_id), "',", ', '.join( ["'" + x + "'" for x in scoreData] )])
	#print 'tmpData =', tmpData   # DEBUG

	cmd = ''.join(["INSERT INTO ", tableName,
						" ( score_id, vocabulary, reading_compreh, reading_total, word_analysis, listening, \n",
						"spelling, capitalization, punct_read_word, usage_expression, language_total, concepts_est, \n",
						"prob_data_interp, mathT_mComput, computation, mathT_pComput, coreT_mComput, coreT_pComput, \n",
						"social_studies, science, maps_diagrams, ref_mtrls, sources_total, composite_mComput, composite_pComput, \n",
						"filler_25, filler_26, rdProfileT_pWords, rdProfileT_mWords, filler_29, filler_30 ) \n",
						" VALUES (", tmpData, ")"])
	#print cmd   # DEBUG
	cursor.execute(cmd)

	Log('After WriteItbsScoreTable(%s), insert' % tableName)

	if len(cursor.connection.messages) > 0:
		msgs = '\n'.join(['Connection Error(s) executing INSERT for table ' + tableName] + cursor.messages)   # DEBUG
		raise Exception(msgs)
	#

	if len(cursor.messages) > 0:
		msgs = '\n'.join(['Cursor Error(s) executing INSERT for table ' + tableName] + cursor.messages)   # DEBUG
		raise Exception(msgs)
	#

	Log('After WriteItbsScoreTable(%s), insert messages check' % tableName)

# End WriteItbsScoreTable()


def WriteItedScoreTable(cursor, scoreData, tableName, dataType):
	# Check for 'tableName' table. If it doesn't exist, create it.
	cursor.execute("show tables;")
	tmpAllTables = cursor.fetchall()            # Returns a list of one-element lists (actually Python tuples).
	allTables = [ x[0] for x in tmpAllTables ]  # Flattens the 2-dim list to one-dim. The data we want is in the first element of each sublist.

	Log('After WriteItedScoreTable(%s), show tables' % tableName)

	if not tableName in allTables:
		# Create the table   ('|' to separate ITBS/ITED where there are differences)
		cmd = ''.join(["CREATE TABLE `", tableName, "` (\n",
							" `score_id`          int(10) unsigned NOT NULL,\n",
							" `vocabulary`        ", dataType, " default 0,\n",
							" `reading_compreh`   ", dataType, " default 0,\n",
							" `reading_total`     ", dataType, " default 0,\n",
							" `filler_4`          ", dataType, " default 0,\n",
							" `filler_5`          ", dataType, " default 0,\n",
							" `spelling`          ", dataType, " default 0,\n",
							" `filler_7`          ", dataType, " default 0,\n",
							" `filler_8`          ", dataType, " default 0,\n",
							" `filler_9`          ", dataType, " default 0,\n",
							" `revise_writ_mtrl`  ", dataType, " default 0,\n",
							" `filler_11`         ", dataType, " default 0,\n",
							" `filler_12`         ", dataType, " default 0,\n",
							" `concepts_probs`    ", dataType, " default 0,\n",
							" `computation`       ", dataType, " default 0,\n",
							" `mathT_pComput`     ", dataType, " default 0,\n",
							" `coreT_mComput`     ", dataType, " default 0,\n",
							" `coreT_pComput`     ", dataType, " default 0,\n",
							" `social_studies`    ", dataType, " default 0,\n",
							" `science`           ", dataType, " default 0,\n",
							" `filler_20`         ", dataType, " default 0,\n",
							" `filler_21`         ", dataType, " default 0,\n",
							" `sources_of_info`   ", dataType, " default 0,\n",
							" `composite_mComput` ", dataType, " default 0,\n",
							" `composite_pComput` ", dataType, " default 0,\n",
							" `filler_25`         ", dataType, " default 0,\n",
							" `filler_26`         ", dataType, " default 0,\n",
							" `filler_27`         ", dataType, " default 0,\n",
							" `filler_28`         ", dataType, " default 0,\n",
							" `filler_29`         ", dataType, " default 0,\n",
							" `filler_30`         ", dataType, " default 0,\n",
							" PRIMARY KEY  (`score_id`)\n)\n",
							" ENGINE=MyISAM  DEFAULT CHARSET=latin1 PACK_KEYS=0"])
		#print cmd   # DEBUG
		cursor.execute(cmd)

		Log('After WriteItedScoreTable(%s), create table' % tableName)

		if len(cursor.connection.messages) > 0:
			msgs = '\n'.join(['Connection Error(s) executing CREATE TABLE for table ' + tableName] + cursor.messages)   # DEBUG
			raise Exception(msgs)
		#

		if len(cursor.messages) > 0:
			msgs = '\n'.join(['Cursor Error(s) executing CREATE TABLE for table ' + tableName] + cursor.messages)   # DEBUG
			raise Exception(msgs)
		#

		Log('After WriteItedScoreTable(%s), create table messsages check' % tableName)

	# End if not table


	# Get the latest score_id to link this table to the score_student_data table
	cursor.execute('select max(score_id) from score_student_data')
	tmpScoreId = cursor.fetchall()
	score_id = tmpScoreId[0][0]

	# Change blank scores to zeros for db int data type
	#print 'scoreData =', str(scoreData)   # DEBUG
	for i in range ( len(scoreData) ):
		if scoreData[i] in ['    ', '   ', '  ', ' ']: scoreData[i] = '0'
	#

	# Add data to the table
	tmpData = ''.join(["'", str(score_id), "',", ', '.join( ["'" + x + "'" for x in scoreData] )])
	#print 'tmpData =', tmpData   # DEBUG

	cmd = ''.join(["INSERT INTO ", tableName,
						" ( score_id, vocabulary, reading_compreh, reading_total, filler_4, filler_5, \n",
						"spelling, filler_7, filler_8, filler_9, revise_writ_mtrl, filler_11, \n",
						"filler_12, concepts_probs, computation, mathT_pComput, coreT_mComput, coreT_pComput, \n",
						"social_studies, science, filler_20, filler_21, sources_of_info, composite_mComput, composite_pComput, \n",
						"filler_25, filler_26, filler_27, filler_28, filler_29, filler_30 ) \n",
						" VALUES (", tmpData, ")"])
	#print cmd   # DEBUG
	cursor.execute(cmd)

	Log('After WriteItedScoreTable(%s), insert' % tableName)

	if len(cursor.connection.messages) > 0:
		msgs = '\n'.join(['Connection Error(s) executing INSERT for table ' + tableName] + cursor.messages)   # DEBUG
		raise Exception(msgs)
	#

	if len(cursor.messages) > 0:
		msgs = '\n'.join(['Cursor Error(s) executing INSERT for table ' + tableName] + cursor.messages)   # DEBUG
		raise Exception(msgs)
	#

	Log('After WriteItedScoreTable(%s), insert messages check' % tableName)

# End WriteItedScoreTable()


#-------------------------------------------------------------------------------
# Program entry point
#-------------------------------------------------------------------------------
if __name__ == '__main__':
	'''
	Parse program args. They are to be combined into ONE arg having the format:
	   "item=data,item=data" with no whitespace.

	E.g.:
	   "data_file=Test_Data.txt,host=net.iche-idaho.org,user=iche,pwd=s1lvercreek,db=iche"

	OPTIONAL: Add console_debug=true as in
	   "data_file=Test_Data.txt,host=net.iche-idaho.org,user=iche,pwd=s1lvercreek,db=iche,console_debug=1"

	For local debug:
	   "data_file=Test_Data.txt,host=localhost,user=HP_Administrator,pwd=hpadmin,db=test_db,console_debug=1"
	'''

	ClearLogFile()

	Log('Entered main')
	Log('Python version:  ' + platform.python_version() )
	Log('MySQLdb version: ' + '.'.join([ str(version_info[0]), str(version_info[1]), str(version_info[2])] ) + ' ' + str(version_info[3]) )

	if version_info != (1, 2, 3, 'final', 0):
		Log('Please upgrade MySQLdb to version 1.2.3')
	#

	bGotDataFile = bGotHost = bGotUser = bGotPwd = bGotDb = False

	'''args = sys.argv[1].split(',')'''
        args = "data_file=Test_Data_2011.txt,host=localhost,user=root,pwd=root,db=iche,console_debug=1".split(',')
	for arg in args:
		argName, argData = arg.split('=')
		if   argName == 'data_file':  dataFile = argData;  bGotDataFile = True
		elif argName == 'host':       db_host = argData;   bGotHost = True
		elif argName == 'user':       db_user = argData;   bGotUser = True
		elif argName == 'pwd':        db_pwd = argData;    bGotPwd = True
		elif argName == 'db':         db_name = argData;   bGotDb = True
		elif argName == 'console_debug':
			if argData == '1':
				bConsoleDebug = True
			else:
				bConsoleDebug = False
		else:
			WriteStatusFile('Invalid arg: ' + argName + '.')
			sys.exit(1)
		#
	#
	if False in [bGotDataFile, bGotHost, bGotUser, bGotPwd, bGotDb]:
		WriteStatusFile('Not all required arg data supplied. (Note: Arg names are case-sensitive).\n'+\
							 'Example: "data_file=Test_Data.txt,host=net.iche-idaho.org,user=iche,pwd=s1lvercreek,db=iche" ')
		sys.exit(1)
	#

	Log('After arg parsing')
	ClearStatusFile()

	try:
		# Connect to MySQL
		db = MySQLdb.connect(host = db_host, user = db_user, passwd = db_pwd, db = db_name)
		cursor = db.cursor()
		Log('After db connect')
		Log('   db     = ' + str(db) ) 
		Log('   cursor = ' + str(cursor) )

		cmd = 'SHOW VARIABLES LIKE "%version%";'
		cursor.execute(cmd)
		mysqlVersionStr = cursor.fetchall()	
		mysqlVersionStrs = [ ': '.join([x[0], x[1]]) for x in mysqlVersionStr ]
		for vstr in mysqlVersionStrs:
			Log('   ' + vstr)
		#

		# Load the Riverside data all into memory; it's small enough to not be a big
		# deal -- 1.5 to 2 MB.
		if not os.path.exists(dataFile):
			msg = "Test data file " + dataFile + " does not exist"
			raise Exception(msg)
		else:
			Log("Test data file " + dataFile + " exits")
		#

		f = open(dataFile, 'r', -1)   # Read mode, fully buffered.
		if f == None:
			msg = "Failed to open test data file " + dataFile
			raise Exception(msg)
		else:
			Log("Opened test data file " + dataFile)
		#

		data = f.read()
		if len(data) == 0:
			msg = "Failed to read test data file " + dataFile
			raise Exception(msg)	
		else:
			Log('After reading Riverside data file: read %d bytes --\n'  % len(data) +\
				 'this might be different than the file size by the number of lines \n' +\
				 'due the way Python reads lines, depending on the newline characters.')
		#
		f.close()

		if not '\n' in data:
			msg = "Test data file does not contain the expected linefeeds for line delimiters"
			raise Exception(msg)
		#

		# Parse the Riverside data
		dataLines = data.split('\n')

		Log("The test data file contains %d students (lines)\n" % len(dataLines) )

		#raise Exception('test') # DEBUG

		lineNum = 0
		for line in dataLines:
			lineNum += 1
			print 'Line', lineNum, 'of', len(dataLines)

			lineParts = line.split(',')

			numLineParts = len(lineParts)
			Log("Line %d has %d fields" % (lineNum, numLineParts))

			if numLineParts < 10:  # There actually should be a lot more that 10 -- but there is a empty line at the end of the data.
				if len(line) > 0:
					msg = "The test data file does not contain the expected commas for field" +\
						 " delimiters within each line, in line %d containing %s" % (lineNum, line)
					raise Exception(msg)	
				else:
					Log("Skipping processing of empty line %d" % lineNum)
					continue
				#
			else:
				Log('About to process Test Data line %d' % lineNum)
			#


			# Get student personal data
			class stuData:
				pass

			stuData.testType   = lineParts[TEST_TYPE]
			stuData.state      = lineParts[STATE]
			stuData.regionNum  = lineParts[BUILDING_NAME].split(' ')[0]   # Region number
			stuData.regionName = lineParts[BUILDING_NAME].split(' ')[1]   # Region name
			stuData.campus     = lineParts[CLASS_NAME][0]                 # Use first letter only
			stuData.grade      = lineParts[GRADE]
			stuData.dateTested = lineParts[DATE_TESTED][4:] + '-' + lineParts[DATE_TESTED][0:2] + '-' + lineParts[DATE_TESTED][2:4]
			stuData.lastName   = lineParts[LAST_NAME]
			stuData.firstName  = lineParts[FIRST_NAME]
			stuData.gender     = lineParts[GENDER]
			stuData.dob        = lineParts[BIRTHDATE][4:] + '-' + lineParts[BIRTHDATE][0:2] + '-' + lineParts[BIRTHDATE][2:4]
			stuData.studentId  = lineParts[STUDENT_ID]
			stuData.level      = lineParts[LEVEL]

			Log('student = %s %s' % (stuData.firstName, stuData.lastName) )

			# Fix stuData items that are blank (2008 Riverside data had some blank dob's)
			# ### This may have to be expanded for future years.... ###
			if stuData.dob == '--': stuData.dob = '0000-00-00'

			# Get student scores
			rawData = SplitFixedWidth( lineParts[RAW_SCORES], 30, 2 )
			stdData = SplitFixedWidth( lineParts[STD_SCORES], 30, 3 )   # Three digits each
			grdData = SplitFixedWidth( lineParts[GRD_SCORES], 30, 4 )   # Four chars each, text (NOT floating-point)
			nprData = SplitFixedWidth( lineParts[NPR_SCORES], 30, 2 )
			nceData = SplitFixedWidth( lineParts[NCE_SCORES], 30, 2 )
			nstData = SplitFixedWidth( lineParts[NST_SCORES], 30, 1 )   # One digit each

			#print str(rawData)   # DEBUG
			#print str(stdData)   # DEBUG
			#print str(grdData)   # DEBUG
			#print str(nprData)   # DEBUG
			#print str(nceData)   # DEBUG
			#print str(nstData)   # DEBUG

			Log('After parsing Riverside data')

			# Write the data into the MySQL database tables
			WriteStudentTable(cursor, stuData, "score_student_data")

			if stuData.testType == 'ITBS':
				WriteItbsScoreTable(cursor, rawData, 'itbs_score_raw',          'int(2) unsigned')
				WriteItbsScoreTable(cursor, stdData, 'itbs_score_std',          'int(3) unsigned')
				WriteItbsScoreTable(cursor, grdData, 'itbs_score_grade_equiv',  'char(4)')
				WriteItbsScoreTable(cursor, nprData, 'itbs_score_npr',          'int(2) unsigned')
				WriteItbsScoreTable(cursor, nceData, 'itbs_score_nce',          'int(2) unsigned')
				WriteItbsScoreTable(cursor, nstData, 'itbs_score_natl_stanine', 'int(1) unsigned')

			elif stuData.testType == 'ITED':
				WriteItedScoreTable(cursor, rawData, 'ited_score_raw',          'int(2) unsigned')
				WriteItedScoreTable(cursor, stdData, 'ited_score_std',          'int(3) unsigned')
				WriteItedScoreTable(cursor, grdData, 'ited_score_grade_equiv',  'char(4)')
				WriteItedScoreTable(cursor, nprData, 'ited_score_npr',          'int(2) unsigned')
				WriteItedScoreTable(cursor, nceData, 'ited_score_nce',          'int(2) unsigned')
				WriteItedScoreTable(cursor, nstData, 'ited_score_natl_stanine', 'int(1) unsigned')

			else:
				WriteStatusFile("Error: Test type is %s, should be one of ITBS, ITED for %s %s, ID: %d" %\
									 (stuData.testType, stuData.firstName, stuData.lastName, stuData.studentId) )
				sys.exit(1)
			#

			Log('After all calls to write tables')
			Log('-' * 80 + '\n') 

		# End for each line

	except MySQLdb.Error, e:
		Log("Exception: error %d; %s" % (e.args[0], e.args[1]))
		WriteStatusFile("Exception: error %d; %s" % (e.args[0], e.args[1]) )
		sys.exit(1)
	#	
	except Exception, e:
		Log('Exception: ' + str(e))
		WriteStatusFile('Exception: ' + str(e) )
		sys.exit(1)
	#
	except:
		WriteStatusFile('Unexpected and unknown exception' )
		sys.exit(1)
	#

	# Close the cursor, commit changes, and close the connection.
	Log('About to close cursor, commit changes, close connection')

	cursor.close()
	db.commit()
	db.close()

	Log('About to write "OK" status')
	WriteStatusFile('OK')
	print 'Finished'
	sys.exit(0)

# End if main


# EOF

