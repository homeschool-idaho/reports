#!/usr/local/bin/python

#-------------------------------------------------------------------------------
#
# parse_riverside_data.py
#
# Copyright 2008 Idaho Coalition of Home Educators (ICHE). All rights reserved.
# Written by Bruce Dickey -- bruce@thedickeys.net.
#
# History
#    2014-Apr-5 MD Removed unused functions and tested
#
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
TEST_TYPE = 1       # 'ITBS' or 'ITED'
STATE = 2
BUILDING_NAME = 7   # Contains both ICHE region number and region name
CLASS_NAME = 9      # ICHE 'Campus'. Is compass directions.
# ICHE uses 'N' 'S' 'E' 'W' instead of spelled out as Riverside does.
GRADE = 11
DATE_TESTED = 12
LAST_NAME = 13
FIRST_NAME = 14
GENDER = 15
BIRTHDATE = 16
STUDENT_ID = 17
LEVEL = 19
RAW_SCORES = 34
STD_SCORES = 35
GRD_SCORES = 36
NPR_SCORES = 38
NCE_SCORES = 40
NST_SCORES = 41

global bConsoleDebug
bConsoleDebug = False

#-------------------------------------------------------------------------------
# Functions
#-------------------------------------------------------------------------------


def ClearLogFile():
    f = file('parse_riverside_data_log.txt', 'w')
    f.close()

# ClearLogFile


def Log(inStr):
    if bConsoleDebug:
        print inStr
    f = file('parse_riverside_data_log.txt', 'a')
    f.write(inStr + '\n')
    f.close()

# Log


def ClearStatusFile():
    f = file('parse_riverside_data_status.txt', 'w')
    f.close()

# ClearStatusFile


def WriteStatusFile(inStr):
    f = file('parse_riverside_data_status.txt', 'a')
    f.write(inStr + '\n')
    f.close()

# WriteStatusFile


def SplitFixedWidth(inStr, numDataItems, dataWidth):
    data = []
    i = 0
    j = dataWidth

    while j < ((numDataItems + 1) * dataWidth):
        data.append(inStr[i:j])
        i += dataWidth
        j += dataWidth
        #

    return data

# SplitFixedWidth


#
#-------------------------------------------------------------------------------
# Program entry point
#-------------------------------------------------------------------------------


if __name__ == '__main__':

    # Parse program args. They are to be combined into ONE arg having the format:
    #    "item=data,item=data" with no whitespace.
    #
    # E.g.:
    #    "data_file=Test_Data.txt,host=net.iche-idaho.org,user=iche,pwd=s1lvercreek,db=iche"
    #
    # OPTIONAL: Add console_debug=true as in
    #    "data_file=Test_Data.txt,host=net.iche-idaho.org,user=iche,pwd=s1lvercreek,db=iche,console_debug=1"
    #
    # For local debug:
    #    "data_file=Test_Data.txt,host=localhost,user=HP_Administrator,pwd=hpadmin,db=test_db,console_debug=1"

    ClearLogFile()

    Log('Entered main')
    Log('Python version:  ' + platform.python_version())
    Log('MySQLdb version: ' + '.'.join([str(version_info[0]), str(version_info[1]), str(version_info[2])]) + ' ' + str(
        version_info[3]))

    if version_info != (1, 2, 3, 'final', 0):
        Log('Please upgrade MySQLdb to version 1.2.2')
        #

    bGotDataFile = bGotHost = bGotUser = bGotPwd = bGotDb = False
    #for local debug
    args = "data_file=scoredata.txt".split(',')
    #args = sys.argv[1].split(',')

    for arg in args:
        argName, argData = arg.split('=')
        if argName == 'data_file':
            dataFile = argData
            bGotDataFile = True
        else:
            WriteStatusFile('Invalid arg: ' + argName + '.')
            sys.exit(1)
            #
            #

    if not bGotDataFile:
        WriteStatusFile('Not all required arg data supplied. (Note: Arg names are case-sensitive)\nExample: "data_file=Test_Data.txt" ')
        sys.exit(1)
        #

    Log('After arg parsing')
    ClearStatusFile()

    try:
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
            Log('After reading Riverside data file: read %d bytes --\n' % len(data) + \
                'this might be different than the file size by the number of lines \n' + \
                'due the way Python reads lines, depending on the newline characters.')
            #
            f.close()

            if not '\n' in data:
                msg = "Test data file does not contain the expected linefeeds for line delimiters"
                raise Exception(msg)
                #

            # Parse the Riverside data
            dataLines = data.split('\n')

            Log("The test data file contains %d students (lines)\n" % len(dataLines))

            #raise Exception('test') # DEBUG

            # Write csv files
            f = open('npr.csv', 'w')
            f.write("first, last, vocabulary, reading_compreh, reading_total, filler_4, filler_5," + \
                    "spelling, filler_7, filler_8, filler_9, revise_writ_mtrl, filler_11," + \
                    "filler_12, concepts_probs, computation, mathT_pComput, coreT_mComput, coreT_pComput," + \
                    "social_studies, science, filler_20, filler_21, sources_of_info, composite_mComput, " + \
                    "composite_pComput," + \
                    "filler_25, filler_26, filler_27, filler_28, filler_29, filler_30")

            fsumma = open('summa.csv', 'w')
            fsumma.write("first, last, vocabulary, reading_compreh, reading_total, filler_4, filler_5," + \
                         "spelling, filler_7, filler_8, filler_9, revise_writ_mtrl, filler_11," + \
                         "filler_12, concepts_probs, computation, mathT_pComput, coreT_mComput, coreT_pComput," + \
                         "social_studies, science, filler_20, filler_21, sources_of_info, composite_mComput, " + \
                         "composite_pComput," + \
                         "filler_25, filler_26, filler_27, filler_28, filler_29, filler_30")

            fwho = open('who.csv', 'w')
            fwho.write("first, last, vocabulary, reading_compreh, reading_total, filler_4, filler_5," + \
                       "spelling, filler_7, filler_8, filler_9, revise_writ_mtrl, filler_11," + \
                       "filler_12, concepts_probs, computation, mathT_pComput, coreT_mComput, " + \
                       "coreT_pComput," + \
                       "social_studies, science, filler_20, filler_21, sources_of_info, composite_mComput, " + \
                       "composite_pComput," + \
                       "filler_25, filler_26, filler_27, filler_28, filler_29, filler_30")

            lineNum = 0
            for line in dataLines:   # For each student
                lineNum += 1
                print 'Line', lineNum, 'of', len(dataLines)

                lineParts = line.split(',')

                numLineParts = len(lineParts)
                Log("Line %d has %d fields" % (lineNum, numLineParts))

                # There actually should be a lot more that 10 -- but there is a empty line at the end of the data.
                if numLineParts < 10:
                    if len(line) > 0:
                        msg = "The test data file does not contain the expected commas for field delimiters within each line, in line %d containing %s" % (lineNum, line)
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

                stuData.testType = lineParts[TEST_TYPE]
                stuData.state = lineParts[STATE]
                stuData.regionNum = lineParts[BUILDING_NAME].split(' ')[0]   # Region number
                stuData.regionName = lineParts[BUILDING_NAME].split(' ')[1]   # Region name
                stuData.campus = lineParts[CLASS_NAME][0]                 # Use first letter only
                stuData.grade = lineParts[GRADE]
                stuData.dateTested = lineParts[DATE_TESTED][4:] + '-' + lineParts[DATE_TESTED][0:2] + '-' + lineParts[DATE_TESTED][2:4]
                stuData.lastName = lineParts[LAST_NAME]
                stuData.firstName = lineParts[FIRST_NAME]
                stuData.gender = lineParts[GENDER]
                stuData.dob = lineParts[BIRTHDATE][4:] + '-' + lineParts[BIRTHDATE][0:2] + '-' + lineParts[BIRTHDATE][2:4]
                stuData.studentId = lineParts[STUDENT_ID]
                stuData.level = lineParts[LEVEL]

                Log('student = %s %s' % (stuData.firstName, stuData.lastName))

                # Fix stuData items that are blank (2008 Riverside data had some blank dob's)
                # ### This may have to be expanded for future years.... ###
                if stuData.dob == '--': stuData.dob = '0000-00-00'

                # Get student scores
                rawData = SplitFixedWidth(lineParts[RAW_SCORES], 30, 2)
                stdData = SplitFixedWidth(lineParts[STD_SCORES], 30, 3)   # Three digits each
                grdData = SplitFixedWidth(lineParts[GRD_SCORES], 30, 4)   # Four chars each, text (NOT floating-point)
                nprData = SplitFixedWidth(lineParts[NPR_SCORES], 30, 2)
                nceData = SplitFixedWidth(lineParts[NCE_SCORES], 30, 2)
                nstData = SplitFixedWidth(lineParts[NST_SCORES], 30, 1)   # One digit each

                print str(rawData)   # DEBUG
                print str(stdData)   # DEBUG
                print str(grdData)   # DEBUG
                print str(nprData)   # DEBUG
                print str(nceData)   # DEBUG
                print str(nstData)   # DEBUG

                Log('After parsing Riverside data')

                line = ','.join([stuData.firstName, stuData.lastName] + nprData + ['\n'])
                f.write(line)

                try:
                    comp = int(nprData[23])
                except:
                    comp = 0
                    print 'Invalid comp for ' + stuData.firstName + ' ' + stuData.lastName + ': |' + str(
                        nprData[23]) + '|'
                    print str(nprData)
                    #

                if comp >= 90:
                    fsumma.write(line)
                    #
                if comp >= 80:
                    fwho.write(line)
                    #

            # End for each line

            f.close()
            fsumma.close()
            f.who.close()

    except MySQLdb.Error, e:
        Log("Exception: error %d; %s" % (e.args[0], e.args[1]))
        WriteStatusFile("Exception: error %d; %s" % (e.args[0], e.args[1]))
        sys.exit(1)
    #
    except Exception, e:
        Log('Exception: ' + str(e))
        WriteStatusFile('Exception: ' + str(e))
        sys.exit(1)
    #
    except:
        WriteStatusFile('Unexpected and unknown exception')
        sys.exit(1)
        #

    Log('About to write "OK" status')
    WriteStatusFile('OK')
    print 'Finished'
    sys.exit(0)

# End if main
# EOF

