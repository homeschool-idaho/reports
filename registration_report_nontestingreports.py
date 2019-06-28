#-------------------------------------------------------------------------------
# DESCRIPTION
#    ICHE Report Generator
#
#    Requires the third-party modules:
#       MySQLdb  -- Python interface to MySQL
#       PyRtf    -- .RTF file generation
#
# LEGAL STATEMENTS
#    Copyright 2008, 2009, 2010, 2011, 2012 Idaho Coalition of Home Educators.
#    All Rights Reserved.
#
# HISTORY
#    Written by Bruce Dickey
#    modified by Mark Duenas
#-------------------------------------------------------------------------------

# Python imports
import sys
import os
import os.path
import platform
import string
import time
import copy
import pickle

# Third-party imports
import MySQLdb
from MySQLdb.release import version_info
from PyRTF import *

# ICHE Imports
from orm import *   # A proprietary Object-Relational Mapper


# Get Date-time stamp
t = time.localtime()
date_stamp = str(t[0]) + '-%02d' % t[1] + '-%02d' % t[2]
date_time_stamp = date_stamp + '_%02d' % t[3] + '-%02d' % t[4]


def ClearLogFile():
   try:
      f = file('./output/testing_report_log.txt', 'w')
      f.close()
   except:
      pass   # Dir or file does not exist -- that is OK
#


def Log(inStr):
   print inStr   # Send to stdout too

   f = file('./output/testing_report_log.txt', 'a')
   f.write(inStr + '\n')
   f.close()
#


def ClearStatusFile():
   try:
      f = file('./output/testing_report_status.txt', 'w')
      f.close()
   except:
      pass   # Dir or file does not exist -- that is OK      
#


def WriteStatusFile(inStr):
   f = file('./output/testing_report_status.txt', 'a')
   f.write(inStr + '\n')
   f.close()
#


def Tab(inches):
   return round(1440 * inches)


def RunQuery(select, where, orderBy, limit):
   query = ['SELECT ']
   selectParts = []
   tableNames = []
   
   for table in select:
      tableName  = table[0]
      tableNames.append(tableName)
      
      columnsStr = table[1]
      tmpColumnsList = columnsStr.split(';')
      columnsList = [ x.strip() for x in tmpColumnsList]
      
      for col in columnsList:
         if not ',' in col: 
            # Build the query string
            selectParts.append( '.'.join([ tableName, col]))
         else:
            # If there is ',' in col, it was passed in a a literal part of the query
            # and does not need to be built.
            selectParts.append(col)
         #
      #
   #
   
   query.append( ', '.join(selectParts) )
   query.append( ' from ')
   query.append( ', '.join(tableNames) )
   if len(where) > 0:
      query.append(' where ')
      query.append(where)
   if len(orderBy) > 0:
      query.append(' order by ')
      query.append(orderBy)
   if len(limit) > 0:
      query.append(' limit ')
      query.append(limit)
   query.append(';')
   queryStr = ''.join(query)
   
   #-------------------
   # Execute the query
   #-------------------
   if 0:
     
      f = open('query.txt', 'a')
      f.write('\n\n')
      f.write(queryStr)
      f.close()
      
      if 0:
         print queryStr         # DEBUG
         print queryStr[100:]   # DEBUG
         print queryStr[200:]   # DEBUG
         print queryStr[300:]   # DEBUG
         print queryStr[400:]   # DEBUG
         print queryStr[500:]   # DEBUG
      #
   #
   
   cursor.execute(queryStr)   # Can take several tens of seconds...
   
   if len(cursor.connection.messages) > 0:
      msgs = '\n'.join(['Connection Error(s) executing INSERT for table ' + tableName] + cursor.messages)   # DEBUG
      raise Exception(msgs)
   #
   
   if len(cursor.messages) > 0:
      msgs = '\n'.join(['Cursor Error(s) executing INSERT for table ' + tableName] + cursor.messages)   # DEBUG
      raise Exception(msgs)
   #
   
   records = cursor.fetchall()
   return records

#  RunQuery()


class region:
   def __init__(self, regionNum):
      self.regionNum = regionNum
      self.families = []
   #
   def AddFamily(self, family):
      self.families.append(family)
   #
#

class family:
   def __init__(self, member):
      self.member = member
      self.payments = [] 
      self.testingStudents = []
   #
   def AddPayment(self, payment):
      self.payments.append(payment)
   #
   def AddTestingStudent(self, testingStudent):
      self.testingStudents.append(testingStudent)
   #
#

def FamilyCmp(family_A, family_B):
   '''
   A comparison method passed to the Python-supplied method 'sorted()', for sorting lists.
   This is for sorting ICHE members by mother's last name, first name for a given region.
   '''
   str_A = family_A.member.mother_l_name + family_A.member.mother_f_name
   str_B = family_B.member.mother_l_name + family_B.member.mother_f_name
   
   str_A = str_A.lower()
   str_B = str_B.lower()
   
   if str_A < str_B:
      return -1
   else:
      return 1
#

def MemberNameCmp(member_A, member_B):
   '''
   A comparison method passed to the Python-supplied method 'sorted()', for sorting lists.
   This is for sorting ICHE members by mother's last name, first name for a given region.
   '''
   str_A = member_A.mother_l_name + member_A.mother_f_name
   str_B = member_B.mother_l_name + member_B.mother_f_name
   
   str_A = str_A.lower()
   str_B = str_B.lower()
   
   if str_A < str_B:
      return -1
   else:
      return 1
#

class testingStudent:
   def __init__(self, student, testing_history):
      self.student = student
      self.testing_history = testing_history
   #
#


def DbGet_FinanceData(cursor, startDate, endDate):

   # To Do -- get data for all members; not just ones with testing students
   
   pass
#


paymentStartDate = None
def DbGet_TestingStudentsByRegionParent(cursor, rptYear):
   global paymentStartDate

   errorCt = 0
   #
   # CHECK for duplicate entries for student_ids. Not proceeding if this is the case.
   #
   # select student_id, COUNT(*) as count from testing_history where test_year = '2009' GROUP BY student_id having count > 1
   #
   tableSelects = ( ('testing_history', 'student_id, COUNT(*) as count'), )
   where = 'testing_history.test_year = "' + str(rptYear) + '" '+\
           'GROUP BY student_id having count > 1'
   s_records = RunQuery(tableSelects, where, orderBy='', limit='10000')
   
   if len(s_records) >= 1:
      print "ERROR -- There are duplicated student_id's in the testing_history table. Each student should appear only once."
      print "         Run the following query to find them:"
      print "         select student_id, COUNT(*) as count from testing_history where test_year = '" + str(rptYear) + "' GROUP BY student_id having count > 1"
      
      for i in s_records:
         print i
         print
      #
      raise Exception("Cannot continue until the above problem is fixed")
   #
   
   # Claude has a web page now at http://www.iche-idaho.org/admin/studentstats.html
   
   #
   # Get testing_history data
   #
   tableSelects = ( ('testing_history', '*'), )
   where = 'testing_history.test_year = "' + str(rptYear) + '" '+\
           ' and payment_id is not NULL'
   th_records = RunQuery(tableSelects, where, orderBy='', limit='10000')
   
   # Run Claude's script to check student & family count:  http://net.iche-idaho.org/count_paid_testers.php
   #
   print 'Read ' + str(len(th_records)) + ' testing_history records'  # DEBUG
   print # DEBUG
   
   testHistObjs = []
   for th_rec in th_records:
      testHistObjs.append(testing_history(th_rec))
   #
   
   
   #
   # Get student data, member data, payment data
   #
   families = {}
   missingMemberIds = []
   
   for testHistObj in testHistObjs:
      tableSelects = ( ('student', '*'), )
      where = 'student.student_id  = "' + str(testHistObj.student_id) + '" '
      s_record = RunQuery(tableSelects, where, orderBy='', limit='10000')
      
      studentObj = student(s_record[0])
      testingStudentObj = testingStudent( studentObj, testHistObj )
      
      member_id = studentObj.member_id
      
      print 'studentObj.member_id =', studentObj.member_id  # DEBUG
      
      
      if not member_id in families.keys():
         #
         # Get member data (single record)
         #
         memberColsList = list(MEMBER_COL_NAMES)
         memberColsList[1] = "if(member.mother_f_name = '',member.father_f_name, member.mother_f_name) as f_name_1"
         memberColsList[2] = "if(member.mother_l_name = '',member.father_l_name, member.mother_l_name) as l_name_1"
         memberColsList[3] = "if(member.father_f_name = '',member.mother_f_name, member.father_f_name) as f_name_1"
         memberColsList[4] = "if(member.father_l_name = '',member.mother_l_name, member.father_l_name) as l_name_1"
         memberCols = '; '.join(memberColsList)
         tableSelects = ( ( 'member', memberCols), )
         where = 'member_id = ' + str(member_id)
         m_record = RunQuery(tableSelects, where, orderBy='', limit='10000')
         
         if len(m_record) == 0:
            print "ERROR -- Record for member with id", member_id, "was not found!"
            missingMemberIds.append( ''.join([ "Missing member_id ", str(member_id), " for student_id ", str(testHistObj.student_id) ]) )
            continue
         #
         
         memberObj = member( m_record[0][0:NUM_MEMBER_COLS])
         familyObj = family(memberObj)
         
         #
         # Get all relevant payment data (should be multiple records; membership,
         # and then a testing fee for each student)
         #
         tableSelects = ( ( 'payment', '*'), )
         paymentStartDate = '-'.join( [str(rptYear-1), '01', '01'])
         where = 'payment.member_id = "' + str(member_id) + '" and date(payment.date_entered) >= "' + paymentStartDate + '"'
         p_records = RunQuery(tableSelects, where, orderBy='', limit='10000')
         
         for p_rec in p_records:
            #print '     ', p_rec # DEBUG
            
            paymentObj = payment( p_rec )
            familyObj.AddPayment(paymentObj)
         #
         #print # DEBUG
         
         families[member_id] = familyObj
         
         if     memberObj.mother_l_name.strip() == "" and memberObj.mother_f_name.strip() == "" \
            and memberObj.father_l_name.strip() == "" and memberObj.father_f_name.strip() == "":
            raise Exception("ERROR -- Missing member parent names. Member ID is " + str(memberObj.member_id) )
         #
      else:
         print 'Member ' + str(member_id) + ' is already in families[]'  # DEBUG
         print # DEBUG
      #
      
      # Add students to the family.
      families[member_id].AddTestingStudent(testingStudentObj)
      
   #  End for each student-tseting_history record
   
   for missing in missingMemberIds:   # DEBUG
      print missing
   #
   print # DEBUG
   if len(missingMemberIds) > 0:
      #raise Exception("ERROR -- Missing member_id's; see above list. Cannot continue until the problem is fixed.")
      pass # ###
   #
   
   #
   # Build data hierarchy to return for use by the RTF generation code.
   # Sort by region first.
   #
   
   regions = [None]*19
   
   for regionNum in range(1,20):   # 1-19 inclusive
      cmd = 'regions[' + str(regionNum - 1) + '] = region(' + str(regionNum) + ')' 
      exec cmd
   #
   
   for a_family in families.values():
      regionList = []
      
      '''
      # Some defensive programming here because some members didn't have region numbers...
      if a_family.member.region != 0:
         regionList.append(a_family.member.region)
      else:
         print 'Missing member.region for', a_family.member.mother_f_name, a_family.member.mother_l_name
      #
      '''
      
      # This function is for testing students report, so get the region from the testing_history table instead of from the member table.
      for a_testingStudent in a_family.testingStudents:
         if a_testingStudent.testing_history.region != 0:   # Make sure there IS a region number
            regionList.append(a_testingStudent.testing_history.region)
         else:
            print 'Missing testing_history.region for testing_history_id', a_testingStudent.testing_history.testing_history_id
         #
      #
      
      print 'Region list = ', regionList # DEBUG
      
      #if len(regionList) > 0:                          ### Orig pre-2010-aug-28
      if len(regionList) > 0 and regionList[0] < 20:
         regionNum = regionList[0]
         regions[regionNum - 1].families.append(a_family)
      else:
         if regionList[0] >= 20:
            msg = "ERROR -- Region is outside the range 1 - 19;  a_family.member_id = " +\
                str(a_family.member_id)
            Log(msg)
            errorCt += 1
         #
      #
      
   # End for families
   
   # Sort families in the given region by last name
   for regionObj in regions:
      regionObj.families = sorted(regionObj.families, FamilyCmp)
   #
   
   # Dump the data to the console for debug
   if True:
      print '----------- Regions Test Debug Output ------------'
      for regionObj in regions:
         print 'Region', regionObj.regionNum
         for familyObj in regionObj.families:
            print "   Mother:", familyObj.member.mother_f_name, familyObj.member.mother_l_name
            for paymentObj in familyObj.payments:
               print '      Payment:', paymentObj.item, paymentObj.amount
            #
            for testingStudentObj in familyObj.testingStudents:
               print '      Student:', testingStudentObj.student.f_name, testingStudentObj.student.l_name
            #
         #
      #
   #
   
   return regions   # A list of regionObj's

#  End DbGet_TestingStudentsByRegionParent()


def DbGet_NonMembersByRegion(cursor, rptYear):
   #
   # Get non-members from yesterday, going back 2 years only
   #
   memberColsList = list(MEMBER_COL_NAMES)
   memberColsList[1] = "if(member.mother_f_name = '',member.father_f_name, member.mother_f_name) as f_name_1"
   memberColsList[2] = "if(member.mother_l_name = '',member.father_l_name, member.mother_l_name) as l_name_1"
   memberColsList[3] = "if(member.father_f_name = '',member.mother_f_name, member.father_f_name) as f_name_1"
   memberColsList[4] = "if(member.father_l_name = '',member.mother_l_name, member.father_l_name) as l_name_1"
   memberCols = '; '.join(memberColsList)
   tableSelects = ( ( 'member', memberCols), )
   
   today = list(time.gmtime())
   for i in range(3,9):
      today[i] = 0   # Zero-out all but date
   #
   twoYearsAgoToday = copy.deepcopy(today)
   twoYearsAgoToday[0] -= 2

   where = 'membership_expires < "' + str(today[0]) + '-' + str(today[1]) + '-' + str(today[2]) +\
           '" and membership_expires >= "' + str(rptYear - 2) + '-01-01"'
   
   #if 0:
   #where = 'membership_expires < "' + str(today[0]) + '-' + str(today[1]) + '-' + str(today[2]) +\
   #        '" and membership_expires >= "' + str(twoYearsAgoToday[0]) + '-' + str(twoYearsAgoToday[1]) + '-' +\
   #        str(twoYearsAgoToday[2]) + '"'
   #
   # NOTE -- Does not support custon date ranges for expired members
   #
   #else:
   #   where = 'membership_expires <= "' + str(rptYear) + '-09-01" and membership_expires >= "' + str(rptYear - 1) + '-05-01"'
   #
   
   nm_records = RunQuery(tableSelects, where, orderBy='', limit='10000')
   
   if len(nm_records) == 0:
      print "ERROR -- No non-members found in the most recent past two years!"
   #
   
   nonmembers = []
   for nm_rec in nm_records:
      nonmemberObj = member( nm_rec[0:NUM_MEMBER_COLS])
   
      if     nonmemberObj.mother_l_name.strip() == "" and nonmemberObj.mother_f_name.strip() == "" \
         and nonmemberObj.father_l_name.strip() == "" and nonmemberObj.father_f_name.strip() == "":
         raise Exception("ERROR -- Missing member parent names. Member ID is " + str(nonmemberObj.member_id) )
      else:
         nonmembers.append(nonmemberObj)
      #   
   #
   
   # Sort by last+first name
   sortedNonmembers = sorted(nonmembers, MemberNameCmp)
   
   # Sort by region, then by last+first name
   regions = {}
   for nm in nonmembers:
      if not nm.region in regions.keys():
         regions[nm.region] = []
      #
      regions[ int(nm.region) ].append(nm)
   #
   
   sortedNonmembersByRegion = {}
   for regionNum in range(1, 20):
      if regions.has_key(regionNum):
         sortedNonmembersByRegion[regionNum] = sorted(regions[regionNum], MemberNameCmp)
      else:
         sortedNonmembersByRegion[regionNum] = []
      #
   #
   
   return sortedNonmembers, sortedNonmembersByRegion   # List, Dict

# End DbGet_NonMembersByRegion()


def DbGet_CurrentMembersByRegion(cursor):
   #
   # Get members as of today
   #
   memberColsList = list(MEMBER_COL_NAMES)
   memberColsList[1] = "if(member.mother_f_name = '',member.father_f_name, member.mother_f_name) as f_name_1"
   memberColsList[2] = "if(member.mother_l_name = '',member.father_l_name, member.mother_l_name) as l_name_1"
   memberColsList[3] = "if(member.father_f_name = '',member.mother_f_name, member.father_f_name) as f_name_1"
   memberColsList[4] = "if(member.father_l_name = '',member.mother_l_name, member.father_l_name) as l_name_1"
   memberCols = '; '.join(memberColsList)
   tableSelects = ( ( 'member', memberCols), )
   
   today = list(time.gmtime())
   for i in range(3,9):
      today[i] = 0   # Zero-out all but date
   #
   
   where = 'membership_expires > "' + str(today[0]) + '-' + str(today[1]) + '-' + str(today[2]) + '"'
   m_records = RunQuery(tableSelects, where, orderBy='', limit='10000')
   
   if len(m_records) == 0:
      print "ERROR -- No current members found!"
   #
   
   members = []
   for m_rec in m_records:
      memberObj = member(m_rec[0:NUM_MEMBER_COLS])
  
      if     memberObj.mother_l_name.strip() == "" and memberObj.mother_f_name.strip() == "" \
         and memberObj.father_l_name.strip() == "" and memberObj.father_f_name.strip() == "":
         raise Exception("ERROR -- Missing member parent names. Member ID is " + str(memberObj.member_id) )
      else:
         members.append(memberObj)
      #
   #
   
   # Sort by last+first name
   sortedMembers = sorted(members, MemberNameCmp)
   
   # Sort by region, then by last+first name
   regions = {}
   for m in members:
      if not m.region in regions.keys():
         regions[m.region] = []
      #
      regions[ int(m.region) ].append(m)
   #
   
   sortedMembersByRegion = {}
   for regionNum in range(1, 20):
      if regions.has_key(regionNum):
         sortedMembersByRegion[regionNum] = sorted(regions[regionNum], MemberNameCmp)
      else:
         sortedMembersByRegion[regionNum] = []
      #
   #
   
   return sortedMembers, sortedMembersByRegion   # List, Dict

# End DbGet_MembersByRegion()


def DbGet_CurrentExpiredMembers(cursor, rptYear):   
   '''
   Current and expired members going back to Jan 1, 2 years prior to the rptYear.
   
   Returns a list sorted alphabetically
   '''
   
   #
   # Get members as of today
   #
   memberColsList = list(MEMBER_COL_NAMES)
   memberColsList[1] = "if(member.mother_f_name = '',member.father_f_name, member.mother_f_name) as f_name_1"
   memberColsList[2] = "if(member.mother_l_name = '',member.father_l_name, member.mother_l_name) as l_name_1"
   memberColsList[3] = "if(member.father_f_name = '',member.mother_f_name, member.father_f_name) as f_name_1"
   memberColsList[4] = "if(member.father_l_name = '',member.mother_l_name, member.father_l_name) as l_name_1"
   memberCols = '; '.join(memberColsList)
   tableSelects = ( ( 'member', memberCols), )
   
   today = list(time.gmtime())
   for i in range(3,9):
      today[i] = 0   # Zero-out all but date
   #
   
   where = 'membership_expires >= "' + str(rptYear - 2) + '-01-01"'          
   m_records = RunQuery(tableSelects, where, orderBy='', limit='10000')
   
   if len(m_records) == 0:
      print "ERROR -- No current+expired members found!"
   #
   
   members = []
   for m_rec in m_records:
      memberObj = member(m_rec[0:NUM_MEMBER_COLS])
   
      if     memberObj.mother_l_name.strip() == "" and memberObj.mother_f_name.strip() == "" \
         and memberObj.father_l_name.strip() == "" and memberObj.father_f_name.strip() == "":
         raise Exception("ERROR -- Missing member parent names. Member ID is " + str(i.member_id) )
      else:
         members.append(memberObj)
      #
   #
   
   # Sort by last+first name
   sortedMembers = sorted(members, MemberNameCmp)
   
   return sortedMembers   # List
   
#  DbGet_CurrentExpiredMembers()



#
# DB Access above
#
# #################################################################################################################
#
# Report Generation below
#


regionNames = ('Panhandle', 'Coeur d`Alene', 'Latah-Clearwater', 'Canyon', 'Ada', 'Elmore', 'Magic Valley',
               'Mini-Cassia', 'Bannock', 'Rexburg', 'Idaho Falls', 'Lewis-Nez Perce', 'White Bird',
               'Gem-Payette', 'Adams-Washington', 'Ponderosa', 'Central Mountain', 'Wood River', 'Owyhee')

monthAbbrNames = ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC')

def memberLine(currentMember, section, ss):
    #name is first on the header
    name = currentMember.mother_l_name + ', ' + currentMember.mother_f_name
    #phone number
    phone = ''
    ph = currentMember.phone_home
    if ph.strip() == '':
        ph = currentMember.phone_work
        if ph.strip() == '':
            ph = '______________'
        else:
            ph += ' (W)'
            #
    else:
        ph += ' (H)'
        #
    if not '_' in ph:
        phone = ph[0:3] + '-' + ph[3:6] + '-' + ph[6:]
        #
    street = currentMember.street.strip()
    p = Paragraph(ss.ParagraphStyles.Normal)
    p.append(r'\fs20\tx%d \tx%d \tx%d \tx%d %s \tab %s \tab %s \tab %d \tab %s \line\tab %s, %s %s \tab %s \line ' %\
             (Tab(2.0), Tab(4.4), Tab(5.9), Tab(6.5),
              name, street, phone, currentMember.region,
              currentMember.membership_expires, currentMember.city.strip(),
              currentMember.state, currentMember.zip, currentMember.email.strip() ))
    section.append(p)


def pageBreak(pageNumber, section, ss):
    p = Paragraph(ss.ParagraphStyles.Normal)
    p.append(r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page ' + str(pageNumber))
    section.append(p)
    section.append(r'\page')


def headerLine(regionNum, section, ss, titleHeader, extraText):
    p = Paragraph(ss.ParagraphStyles.Normal)
    p.append(TEXT(titleHeader, size=24, bold=True))
    p.append(TEXT(r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False))
    #p.append(TEXT(r'\tab   %d %s \line ' % (regionNum, regionNames[regionNum - 1]), size=24, bold=True))
    p.append(TEXT(r'\tab   %d %s %s' % (regionNum, regionNames[regionNum - 1], extraText), size=24, bold=True))
    section.append(p)
    p = Paragraph(ss.ParagraphStyles.Normal)
    p.append(
        r'\pard\tx%d \tx%d \tx%d \tx%d \ulw\b\fs20 Name \tab Address \tab Phone/Email \tab Region \tab Expires\line ' %\
        ( Tab(2.0), Tab(4.4), Tab(5.9), Tab(6.5) ))
    section.append(p)

def SummaryReport(sortedMembersByRegion, title, folderName, fileName):
    errorCt = 0

    # Margins are top, left, bottom, right
    regRptMargins = MarginsPropertySet(top=1000, left=720, bottom=720, right=720)

    # Write the report
    combinedDoc = Document()
    ss  = combinedDoc.StyleSheet
    section = Section(paper=None, margins=regRptMargins, break_type=3, headery=None, footery=0, landscape=False) #, first_page_number=pageNum)
    combinedDoc.Sections.append( section )

    maxPageLines          = 51
    numRegionHeaderLines  = 4
    numMemberLines        = 3
    pageNumber            = 1

    linesLeftOnThisPage = maxPageLines

    for regionNum in range(1, 20):

        if regionNum > 1:
            pageBreak(pageNumber, section, ss)
            pageNumber += 1
            linesLeftOnThisPage = maxPageLines

        headerLine(regionNum, section, ss, title, '')
        linesLeftOnThisPage -= numRegionHeaderLines

        curMemberCt = len(sortedMembersByRegion[regionNum])
        curMemberNum =0
        for currentMember in sortedMembersByRegion[regionNum]:
            #track the member number (count)
            curMemberNum += 1

            if linesLeftOnThisPage > 4:
                memberLine(currentMember, section, ss)
                linesLeftOnThisPage -= numMemberLines

            if linesLeftOnThisPage < 4:
               if curMemberNum < curMemberCt:
                  pageBreak(pageNumber, section, ss)
                  pageNumber += 1
                  linesLeftOnThisPage = maxPageLines
            #

               if curMemberNum < curMemberCt:
                  headerLine(regionNum, section, ss, title, '(continued)')
                  linesLeftOnThisPage -= numRegionHeaderLines
            #

        try:
            os.mkdir('./output/')
        except:
            pass
            #
        try:
            os.mkdir(folderName)
        except:
            pass
            #

    fileName = fileName + date_time_stamp + '.rtf'

    # Render and print the RTF
    DR = Renderer()                                           # From PyRTF
    DR.Write( combinedDoc, file( fileName, 'w' ) )

    #----------------------------------------------------------------------------
    # Final error count
    #
    print 'CurrentMemberSummaryReport Error count =', errorCt

#  SummaryReport()

def CurrentMemberSummaryReport(sortedMembersByRegion):
    folderName = './output/'
    fileName = './output/CurrentMemberSummaryByRegion_'
    title = 'ICHE Current Members by Region '
    SummaryReport(sortedMembersByRegion, title, folderName, fileName)

def ExpiredMemberSummaryReport(sortedNonMembersByRegion):
    folderName = './output/'
    fileName = './output/ExpiredMemberSummaryByRegion_'
    title = 'ICHE Expired Members by Region '
    SummaryReport(sortedNonMembersByRegion, title, folderName, fileName)


def ByRegionReports(sortedMembersByRegion, title, folderName, fileName):
    errorCt = 0

    # Margins are top, left, bottom, right
    regRptMargins = MarginsPropertySet(top=1000, left=720, bottom=720, right=720)

    maxPageLines          = 51
    numRegionHeaderLines  =  4
    numRegionFooterLines  =  3
    numMemberLines        =  3
    bAddedPageBreak       = False

    for regionNum in range(1, 20):
        linesLeftOnThisPage = maxPageLines

        regionDoc = Document()
        ss = regionDoc.StyleSheet
        pageNumber = 1

        # Create a new section for each region
        section = Section(paper=None, margins=regRptMargins, break_type=3, headery=None, footery=0, landscape=False) #, first_page_number=pageNum)
        regionDoc.Sections.append( section )

        headerLine(regionNum, section, ss, title, '')
        linesLeftOnThisPage -= numRegionHeaderLines

        curMemberCt = len(sortedMembersByRegion[regionNum])
        curMemberNum =0
        for currentMember in sortedMembersByRegion[regionNum]:
            #track the member number (count)
            curMemberNum += 1

            if linesLeftOnThisPage > 4:
                memberLine(currentMember, section, ss)
                linesLeftOnThisPage -= numMemberLines

            if linesLeftOnThisPage < 4:
                if curMemberNum < curMemberCt:
                    pageBreak(pageNumber, section, ss)
                    pageNumber += 1
                    linesLeftOnThisPage = maxPageLines
                    #

                if curMemberNum < curMemberCt:
                    headerLine(regionNum, section, ss, title, '(continued)')
                    linesLeftOnThisPage -= numRegionHeaderLines
                    #

        try:
            os.mkdir('./output/')
        except:
            pass
            #
        try:
            os.mkdir(folderName)
        except:
            pass
            #

        filename = fileName % (regionNum)
        filename += date_time_stamp + '.rtf'

        # Render and print the RTF
        DR = Renderer()                                        # From PyRTF
        DR.Write( regionDoc, file( filename, 'w' ) )

    #----------------------------------------------------------------------------
    # Final error count
    #
    print 'ByRegionReports Error count =', errorCt

#  ByRegionReports()

def CurrentMemberByRegionReports(sortedMembersByRegion):
    title = 'ICHE Current Members by Region '
    folderName = './output/CurrentMembersByRegion/'
    fileName = './output/CurrentMembersByRegion/CurrentMembersForRegion%d_'
    # call the ByRegionReports
    ByRegionReports(sortedMembersByRegion, title, folderName, fileName)

def ExpiredMemberByRegionReports(sortedNonMembersByRegion):
    title = 'ICHE Expired Members by Region '
    folderName = './output/ExpiredMembersByRegion/'
    fileName = './output/ExpiredMembersByRegion/ExpiredMembersForRegion%d_'
    # call the ByRegionReports
    ByRegionReports(sortedNonMembersByRegion, title, folderName, fileName)

#---------------------------
# Alpha-sorted lists
#---------------------------
def headerLineSortedRpt(section, ss, title):
    p = Paragraph(ss.ParagraphStyles.Normal)
    #p.append(TEXT(r'ICHE Current Members ' + title, size=24, bold=True))
    p.append(TEXT(title, size=24, bold=True))
    p.append(TEXT(r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False))
    section.append(p)
    p = Paragraph(ss.ParagraphStyles.Normal)
    p.append(
        r'\pard\tx%d \tx%d \tx%d \tx%d \ulw\b\fs20 Name \tab Address \tab Phone/Email \tab Region \tab Expires\line ' %\
        ( Tab(2.0), Tab(4.4), Tab(5.9), Tab(6.5) ))
    section.append(p)

def SummaryReportAlphaSorted(sortedMembers, title, folderName, fileName, rptYear, isCurrentMembers):
    errorCt = 0

    # Margins are top, left, bottom, right
    regRptMargins = MarginsPropertySet(top=1000, left=720, bottom=720, right=720)

    # Write the report
    combinedDoc = Document()
    ss  = combinedDoc.StyleSheet
    section = Section(paper=None, margins=regRptMargins, break_type=3, headery=None, footery=0, landscape=False) #, first_page_number=pageNum)
    combinedDoc.Sections.append( section )

    maxPageLines          = 51
    numRegionHeaderLines  = 4
    numMemberLines        = 3
    pageNumber            = 1

    linesLeftOnThisPage = maxPageLines
    headerLineSortedRpt(section, ss, title)
    linesLeftOnThisPage -= numRegionHeaderLines

    curMemberCt = len(sortedMembers)
    curMemberNum =0
    for currentMember in sortedMembers:
        #track the member number (count)
        curMemberNum += 1

        if linesLeftOnThisPage > 4:
            memberLine(currentMember, section, ss)
            linesLeftOnThisPage -= numMemberLines

        if linesLeftOnThisPage < 4:
            if curMemberNum < curMemberCt:
                pageBreak(pageNumber, section, ss)
                pageNumber += 1
                linesLeftOnThisPage = maxPageLines
                #

            if curMemberNum < curMemberCt:
                headerLineSortedRpt(section, ss, title)
                linesLeftOnThisPage -= numRegionHeaderLines
                #

    try:
        os.mkdir('./output/')
    except:
        pass
        #
    try:
        os.mkdir(folderName)
    except:
        pass
        #

    p = Paragraph( ss.ParagraphStyles.Normal )
    if isCurrentMembers == 0:
        p.append( '\line \line \line Total current members as of %s: %d' % (date_stamp, len(sortedMembers)) )
    if isCurrentMembers == 1:
        p.append( '\line \line \line Total expired members whose membership expires after Jan 1, %d: %d' % (rptYear-1, len(sortedMembers)) )
    if isCurrentMembers == 2:
        p.append( '\line \line \line Total current and expired members whose membership expires after Jan 1, %d: %d' % (rptYear - 1, len(sortedMembers)) )
    section.append(p)

    fileName = fileName + date_time_stamp + '.rtf'

    # Render and print the RTF
    DR = Renderer()                                           # From PyRTF
    DR.Write( combinedDoc, file( fileName, 'w' ) )

    #----------------------------------------------------------------------------
    # Final error count
    #
    print 'CurrentMemberSummaryReport Error count =', errorCt

#def SummaryReportAlphaSorted(sortedMembers, title, folderName, fileName, rptYear, isCurrentMembers):

def CurrentMembersReportAlphaSorted(sortedMembers):
    title = 'ICHE Current Members Alpha-Sorted'
    folderName = './output/MembersAlphaSortedReports/'
    fileName = './output/MembersAlphaSortedReports/CurrentMembersAlphaSorted_'
    rptYear = 0 #this doesn't matter for the current because it uses a timestamp
    SummaryReportAlphaSorted(sortedMembers, title, folderName, fileName, rptYear, 0)

def ExpiredMembersReportAlphaSorted(sortedMembers, rptYear):
    title = 'ICHE Expired Members Alpha-Sorted'
    folderName = './output/MembersAlphaSortedReports/'
    fileName = './output/MembersAlphaSortedReports/ExpiredMembersAlphaSorted_'
    SummaryReportAlphaSorted(sortedMembers, title, folderName, fileName, rptYear, 1)

def CurrentAndExpiredMembersReportAlphaSorted(sortedMembers, rptYear):
    title = 'ICHE Current and Expired Members Alpha-Sorted'
    folderName = './output/MembersAlphaSortedReports/'
    fileName = './output/MembersAlphaSortedReports/CurrentAndExpiredMembersAlphaSorted_'
    SummaryReportAlphaSorted(sortedMembers, title, folderName, fileName, rptYear, 2)

def CurrentMembersReportAlphaSortedOld(sortedMembers):
   '''
   Alpha sorted
   '''
   
   errorCt = 0
   
   # Write the report
   combinedDoc = Document()
   ss  = combinedDoc.StyleSheet
   
   # Margins are top, left, bottom, right
   regRptMargins = MarginsPropertySet(top=1000, left=720, bottom=720, right=720)
   
   maxPageLines          = 51
   numRegionHeaderLines  =  4
   numRegionFooterLines  =  3
   numMemberLines        =  3
   bAddedPageBreak       = False
   pageNumber            = 1
   
   #for regionNum in range(1, 20):
   
   linesLeftOnThisPage = maxPageLines
   
   #regionDoc = Document()
   
   # Create a new section for each region
   section = Section(paper=None, margins=regRptMargins, break_type=3, headery=None, footery=0, landscape=False) #, first_page_number=pageNum)
   combinedDoc.Sections.append( section )
   #regionDoc.Sections.append( section )

   headerLineSortedRpt(section, ss)
   
   linesLeftOnThisPage -= numRegionHeaderLines

   memberCt = len(sortedMembers)
   memberNum =0
   
   for member in sortedMembers:
      memberNum += 1
      name = member.mother_l_name + ', ' + member.mother_f_name
      
      ph = member.phone_home
      if ph.strip() == '':
         ph = member.phone_work
         if ph.strip() == '':
            ph = '______________'
         else:
            ph += ' (W)'
         #
      else:
         ph += ' (H)'
      #
      
      if not '_' in ph:   
         phone = ph[0:3] + '-' + ph[3:6] + '-' + ph[6:]
      #
      
      # Change street to CapWords
      #streetParts = member.street
      #for part in streetParts:
         #if part != 'PO':
            #part.capitalize()
      ##
      #street = ''.join(streetParts)
      #street = string.capwords(member.street)
      street = member.street.strip()
      
      p = Paragraph( ss.ParagraphStyles.Normal )
      p.append( r'\fs20\tx%d \tx%d \tx%d \tx%d %s \tab %s \tab %s \tab %d \tab %s \line\tab %s, %s %s \tab %s \line ' %\
                      (Tab(2.0), Tab(4.4), Tab(5.9), Tab(6.5),
                      name, street, phone, member.region, 
                      member.membership_expires, member.city.strip(), 
                      member.state, member.zip, member.email.strip() ) )
      section.append(p)
      
      linesLeftOnThisPage -= numMemberLines
      
      bAddedPageBreak = False
      
      if linesLeftOnThisPage < 4:
         
         if memberNum < memberCt:
            p = Paragraph( ss.ParagraphStyles.Normal )
            p.append(r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page ' + str(pageNumber))
            section.append(p)
            section.append(r'\page')
            pageNumber += 1
            linesLeftOnThisPage = maxPageLines
            bAddedPageBreak = True
         #
         
         if memberNum < memberCt:
            p = Paragraph( ss.ParagraphStyles.Normal )
            p.append( TEXT( r'ICHE Current Members', size=24, bold=True) )
            p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
            section.append(p) 
            
            p = Paragraph( ss.ParagraphStyles.Normal )
            p.append( r'\pard\tx%d \tx%d \tx%d \tx%d \ulw\b\fs20 Name \tab Address \tab Phone \tab Region \tab Expires\line ' %\
                      ( Tab(2.2), Tab(4.4), Tab(5.9), Tab(6.5) ) )
            section.append(p)
            linesLeftOnThisPage -= numRegionHeaderLines
         #
      #
      
   # For member
   
   #if not bAddedPageBreak:
   #   p = Paragraph( ss.ParagraphStyles.Normal )
   #   p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
   #   section.append(p)
   #

   p = Paragraph( ss.ParagraphStyles.Normal )
   p.append( '\line \line \line Total current members as of %s: %d' % (date_stamp, len(sortedMembers)) )
   section.append(p) 
   
   try:
      os.mkdir('./output/')
   except:
      pass
   #
   try:
      os.mkdir('./output/CurrentExpiredMembers/')
   except:
      pass
   #
   
   #filename = './output/CurrentExpiredMembersByRegion/CurrentExpiredMembers_' % (regionNum)
   #filename += date_time_stamp + '.rtf'
   
   ## Render and print the RTF
   #DR = Renderer()                                        # From PyRTF
   #DR.Write( regionDoc, file( filename, 'w' ) )

   ## For regionNum
   
   filename = './output/CurrentExpiredMembers/CurrentMembersAlphaSorted_' + date_time_stamp + '.rtf'
   
   # Render and print the RTF
   DR = Renderer()                                           # From PyRTF
   DR.Write( combinedDoc, file( filename, 'w' ) )
   
   #----------------------------------------------------------------------------
   # Final error count
   #
   print 'CurrentMembersAlphaSorted Error count =', errorCt
   
# CurrentMembersReportAlphaSorted()


def ExpiredMembersReportAlphaSortedOld(sortedMembers, rptYear):
   '''
   Alpha sorted
   '''
   
   errorCt = 0
   
   # Write the report
   combinedDoc = Document()
   ss  = combinedDoc.StyleSheet
   
   # Margins are top, left, bottom, right
   regRptMargins = MarginsPropertySet(top=1000, left=720, bottom=720, right=720)
   
   maxPageLines          = 51
   numRegionHeaderLines  =  4
   numRegionFooterLines  =  3
   numMemberLines        =  3
   bAddedPageBreak       = False
   
   #for regionNum in range(1, 20):
   
   linesLeftOnThisPage = maxPageLines
   
   #regionDoc = Document()
   
   # Create a new section for each region
   section = Section(paper=None, margins=regRptMargins, break_type=3, headery=None, footery=0, landscape=False) #, first_page_number=pageNum)
   combinedDoc.Sections.append( section )
   #regionDoc.Sections.append( section )
   
   p = Paragraph( ss.ParagraphStyles.Normal )
   p.append( TEXT( r'ICHE Expired Members ', size=24, bold=True) )
   p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
   #p.append( TEXT( r'\tab   %d %s \line ' % (regionNum, regionNames[regionNum - 1]), size=24, bold=True) )
   section.append(p)
   
   p = Paragraph( ss.ParagraphStyles.Normal )
   p.append( r'\pard\tx%d \tx%d \tx%d \tx%d \ulw\b\fs20 Name \tab Address \tab Phone/Email \tab Region \tab Expires\line ' %\
             ( Tab(2.0), Tab(4.4), Tab(5.9), Tab(6.5) ) )
   section.append(p)
   
   linesLeftOnThisPage -= numRegionHeaderLines
   
   
   memberCt = len(sortedMembers)
   memberNum =0
   
   for member in sortedMembers:
      memberNum += 1
      name = member.mother_l_name + ', ' + member.mother_f_name
      
      ph = member.phone_home
      if ph.strip() == '':
         ph = member.phone_work
         if ph.strip() == '':
            ph = '______________'
         else:
            ph += ' (W)'
         #
      else:
         ph += ' (H)'
      #
      
      if not '_' in ph:   
         phone = ph[0:3] + '-' + ph[3:6] + '-' + ph[6:]
      #
      
      # Change street to CapWords
      #streetParts = member.street
      #for part in streetParts:
         #if part != 'PO':
            #part.capitalize()
      ##
      #street = ''.join(streetParts)
      #street = string.capwords(member.street)
      street = member.street.strip()
      
      p = Paragraph( ss.ParagraphStyles.Normal )
      p.append( r'\fs20\tx%d \tx%d \tx%d \tx%d %s \tab %s \tab %s \tab %d \tab %s \line\tab %s, %s %s \tab %s \line ' %\
                      (Tab(2.0), Tab(4.4), Tab(5.9), Tab(6.5),
                      name, street, phone, member.region, 
                      member.membership_expires, member.city.strip(), 
                      member.state, member.zip, member.email ) )
      section.append(p)
      
      linesLeftOnThisPage -= numMemberLines
      
      bAddedPageBreak = False
      
      if linesLeftOnThisPage < 4:
         
         if memberNum < memberCt:
            p = Paragraph( ss.ParagraphStyles.Normal )
            p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
            section.append(p)
            
            section.append(r'\page')
            
            linesLeftOnThisPage = maxPageLines
            bAddedPageBreak = True
         #
         
         if memberNum < memberCt:
            p = Paragraph( ss.ParagraphStyles.Normal )
            p.append( TEXT( r'ICHE Expired Members', size=24, bold=True) )
            p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
            #p.append( TEXT( r'\tab   %d %s \line ' % (regionNum, regionNames[regionNum - 1]), size=24, bold=True) )
            section.append(p) 
            
            p = Paragraph( ss.ParagraphStyles.Normal )
            p.append( r'\pard\tx%d \tx%d \tx%d \tx%d \ulw\b\fs20 Name \tab Address \tab Phone \tab Region \tab Expires\line ' %\
                      ( Tab(2.2), Tab(4.4), Tab(5.9), Tab(6.5) ) )
            section.append(p)               
         #
      #
      
   # For member
   
   if not bAddedPageBreak:
      p = Paragraph( ss.ParagraphStyles.Normal )
      p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
      section.append(p)
   #

   p = Paragraph( ss.ParagraphStyles.Normal )
   p.append( '\line \line \line Total expired members whose membership expires after Jan 1, %d: %d' % (rptYear-1, len(sortedMembers)) )
   section.append(p) 
   
   try:
      os.mkdir('./output/')
   except:
      pass
   #
   try:
      os.mkdir('./output/CurrentExpiredMembers/')
   except:
      pass
   #
   
   #filename = './output/CurrentExpiredMembersByRegion/CurrentExpiredMembers_' % (regionNum)
   #filename += date_time_stamp + '.rtf'
   
   ## Render and print the RTF
   #DR = Renderer()                                        # From PyRTF
   #DR.Write( regionDoc, file( filename, 'w' ) )

   ## For regionNum
   
   filename = './output/CurrentExpiredMembers/ExpiredMembersAlphaSorted_' + date_time_stamp + '.rtf'
   
   # Render and print the RTF
   DR = Renderer()                                           # From PyRTF
   DR.Write( combinedDoc, file( filename, 'w' ) )
   
   #----------------------------------------------------------------------------
   # Final error count
   #
   print 'ExpiredMembersAlphaSorted Error count =', errorCt
   
# ExpiredMembersReportAlphaSorted()


def CurrentExpiredMembersReportAlphaSorted(currentExpiredMembers, rptYear):
   '''
   Alpha sorted
   '''
   
   errorCt = 0
   
   # Write the report
   combinedDoc = Document()
   ss  = combinedDoc.StyleSheet
   
   # Margins are top, left, bottom, right
   regRptMargins = MarginsPropertySet(top=1000, left=720, bottom=720, right=720)
   
   maxPageLines          = 51
   numRegionHeaderLines  =  4
   numRegionFooterLines  =  3
   numMemberLines        =  3
   bAddedPageBreak       = False
   
   #for regionNum in range(1, 20):
   
   linesLeftOnThisPage = maxPageLines
   
   #regionDoc = Document()
   
   # Create a new section for each region
   section = Section(paper=None, margins=regRptMargins, break_type=3, headery=None, footery=0, landscape=False) #, first_page_number=pageNum)
   combinedDoc.Sections.append( section )
   #regionDoc.Sections.append( section )
   
   p = Paragraph( ss.ParagraphStyles.Normal )
   p.append( TEXT( r'ICHE Current and Expired Members ', size=24, bold=True) )
   p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
   #p.append( TEXT( r'\tab   %d %s \line ' % (regionNum, regionNames[regionNum - 1]), size=24, bold=True) )
   section.append(p)
   
   p = Paragraph( ss.ParagraphStyles.Normal )
   p.append( r'\pard\tx%d \tx%d \tx%d \tx%d \ulw\b\fs20 Name \tab Address \tab Phone/Email \tab Region \tab Expires\line ' %\
             ( Tab(2.0), Tab(4.4), Tab(5.9), Tab(6.5) ) )
   section.append(p)
   
   linesLeftOnThisPage -= numRegionHeaderLines
   
   
   memberCt = len(currentExpiredMembers)
   memberNum =0
   
   for member in currentExpiredMembers:
      memberNum += 1
      name = member.mother_l_name + ', ' + member.mother_f_name
      
      ph = member.phone_home
      if ph.strip() == '':
         ph = member.phone_work
         if ph.strip() == '':
            ph = '______________'
         else:
            ph += ' (W)'
         #
      else:
         ph += ' (H)'
      #
      
      if not '_' in ph:   
         phone = ph[0:3] + '-' + ph[3:6] + '-' + ph[6:]
      #
      
      # Change street to CapWords
      #streetParts = member.street
      #for part in streetParts:
         #if part != 'PO':
            #part.capitalize()
      ##
      #street = ''.join(streetParts)
      #street = string.capwords(member.street)
      street = member.street.strip()
      
      p = Paragraph( ss.ParagraphStyles.Normal )
      p.append( r'\fs20\tx%d \tx%d \tx%d \tx%d %s \tab %s \tab %s \tab %d \tab %s \line\tab %s, %s %s \tab %s \line ' %\
                      (Tab(2.0), Tab(4.4), Tab(5.9), Tab(6.5),
                      name, street, phone, member.region, 
                      member.membership_expires, member.city.strip(), 
                      member.state, member.zip, member.email.strip() ) )
      section.append(p)
      
      linesLeftOnThisPage -= numMemberLines
      
      bAddedPageBreak = False
      
      if linesLeftOnThisPage < 4:
         
         if memberNum < memberCt:
            p = Paragraph( ss.ParagraphStyles.Normal )
            p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
            section.append(p)
            
            section.append(r'\page')
            
            linesLeftOnThisPage = maxPageLines
            bAddedPageBreak = True
         #
         
         if memberNum < memberCt:
            p = Paragraph( ss.ParagraphStyles.Normal )
            p.append( TEXT( r'ICHE Current and Expired Members', size=24, bold=True) )
            p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
            #p.append( TEXT( r'\tab   %d %s \line ' % (regionNum, regionNames[regionNum - 1]), size=24, bold=True) )
            section.append(p) 
            
            p = Paragraph( ss.ParagraphStyles.Normal )
            p.append( r'\pard\tx%d \tx%d \tx%d \tx%d \ulw\b\fs20 Name \tab Address \tab Phone \tab Region \tab Expires\line ' %\
                      ( Tab(2.2), Tab(4.4), Tab(5.9), Tab(6.5) ) )
            section.append(p)               
         #
      #
      
   # For member
   
   if not bAddedPageBreak:
      p = Paragraph( ss.ParagraphStyles.Normal )
      p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
      section.append(p)
   #

   p = Paragraph( ss.ParagraphStyles.Normal )
   p.append( '\line \line \line Total current and expired members whose membership expires after Jan 1, %d: %d' % (rptYear - 1, len(currentExpiredMembers)) )
   section.append(p) 
   
   try:
      os.mkdir('./output/')
   except:
      pass
   #
   try:
      os.mkdir('./output/CurrentExpiredMembers/')
   except:
      pass
   #
   
   #filename = './output/CurrentExpiredMembersByRegion/CurrentExpiredMembers_' % (regionNum)
   #filename += date_time_stamp + '.rtf'
   
   ## Render and print the RTF
   #DR = Renderer()                                        # From PyRTF
   #DR.Write( regionDoc, file( filename, 'w' ) )

   ## For regionNum
   
   filename = './output/CurrentExpiredMembers/CurrentExpiredMembersAlphaSorted_' + date_time_stamp + '.rtf'
   
   # Render and print the RTF
   DR = Renderer()                                           # From PyRTF
   DR.Write( combinedDoc, file( filename, 'w' ) )
   
   #----------------------------------------------------------------------------
   # Final error count
   #
   print 'CurrentExpiredMembersAlphaSorted Error count =', errorCt
   
# CurrentExpiredMembersReportAlphaSorted()


#-------------------------------------------------------------------------------
if __name__ == '__main__' :
   '''
   Expects a CSV string (no spaces) as input, e.g.:
   
   host=net.iche-idaho.org,user=iche,pwd=s1lvercreek,db=iche,rpt_year=2009,cachedDb=0
   
   IMPORTANT: The rpt_year is the year of testing; e.g. If you are running the report
              in 2010 for testing counts for 2011, use 2011 as the rpt_year.
   
   The last parameter is optional and defaults to False. The other are all
   required.
   '''
   startTime = time.time()
   
   ClearLogFile()
   ClearStatusFile()

   bGotHost = bGotUser = bGotPwd = bGotDb = bGotRptYear = False
   bCachedDb = False
   
   args = sys.argv[1].split(',')
   for arg in args:
      argName, argData = arg.split('=')
      if   argName == 'host':       db_host = argData;   bGotHost = True
      elif argName == 'user':       db_user = argData;   bGotUser = True
      elif argName == 'pwd':        db_pwd  = argData;   bGotPwd = True
      elif argName == 'db':         db_name = argData;   bGotDb = True
      elif argName == 'rpt_year':   rptYear = int(argData);   bGotRptYear = True
      elif argName == 'cachedDb':   bCachedDb = int(argData)
      else:
         WriteStatusFile('Invalid arg: ' + argName + '.')
         sys.exit(1)
      #
   #
   
   # Check for required params
   if False in [bGotHost, bGotUser, bGotPwd, bGotDb, bGotRptYear]:
      WriteStatusFile('Not all required arg data supplied. (Note: Arg names are case-sensitive).\n'+\
                      'Example: "host=net.iche-idaho.org,user=iche,pwd=s1lvercreek,db=iche,rpt_year=2012" ')
      sys.exit(1)
   #
   
   
   #-------------------------
   # Connect to MySQL
   #-------------------------
   db = MySQLdb.connect(host = db_host, user = db_user, passwd = db_pwd, db = db_name)
   cursor = db.cursor()
   
   #---------------------------------------
   # Generate Reports Not Involving Testing
   #---------------------------------------
   
   #----------------------------------------------------------------------------
   # MEMBERS Get database data and generate the report .RTF's
   if bCachedDb:
      pkl_file = open('cacheDb/sortedMembers.pkl', 'rb')
      sortedMembers = pickle.load(pkl_file)
      pkl_file.close()
      
      pkl_file = open('cacheDb/sortedMembersByRegion.pkl', 'rb')
      sortedMembersByRegion = pickle.load(pkl_file)
      pkl_file.close()
   else:
      sortedMembers, sortedMembersByRegion = DbGet_CurrentMembersByRegion(cursor)     # Returns a list, a dict of lists
      
      pkl_file = open('cacheDb/sortedMembers.pkl', 'wb')
      pickle.dump(sortedMembers, pkl_file)
      pkl_file.close()
      
      pkl_file = open('cacheDb/sortedMembersByRegion.pkl', 'wb')
      pickle.dump(sortedMembersByRegion, pkl_file)
      pkl_file.close()
   #

   #these are both by region
   CurrentMembersReportAlphaSorted(sortedMembers)                        # Done
   CurrentMemberByRegionReports(sortedMembersByRegion)                   # Done
   CurrentMemberSummaryReport(sortedMembersByRegion)                     # Done
   #CurrentMemberLabels()                                                # TODO
   
   #----------------------------------------------------------------------------
   # NON-MEMBERS Get database data and generate the report .RTF's
   if bCachedDb:
      pkl_file = open('cacheDb/sortedNonmembers.pkl', 'rb')
      sortedNonmembers = pickle.load(pkl_file)
      pkl_file.close()
      
      pkl_file = open('cacheDb/sortedNonmembersByRegion.pkl', 'rb')
      sortedNonmembersByRegion = pickle.load(pkl_file)
      pkl_file.close()
   else:
      sortedNonmembers, sortedNonmembersByRegion = DbGet_NonMembersByRegion(cursor, rptYear)   # Returns a list, a dict of lists
      
      pkl_file = open('cacheDb/sortedNonmembers.pkl', 'wb')
      pickle.dump(sortedNonmembers, pkl_file)
      pkl_file.close()
      
      pkl_file = open('cacheDb/sortedNonmembersByRegion.pkl', 'wb')
      pickle.dump(sortedNonmembersByRegion, pkl_file)
      pkl_file.close()
   #
   
   ExpiredMembersReportAlphaSorted(sortedNonmembers, rptYear)           # Done
   ExpiredMemberByRegionReports(sortedNonmembersByRegion)               # Done
   ExpiredMemberSummaryReport(sortedNonmembersByRegion)                 # Done
   #Obsoleted 3.13.13
   #ExpiredMemberReports(sortedNonmembersByRegion)                       # Done (Summary and by-region files)

   
   #----------------------------------------------------------------------------
   # Curent and expired members: Get database data and generate the report .RTF's
   if bCachedDb:
      pkl_file = open('cacheDb/currentExpiredMembers.pkl', 'rb')
      currentExpiredMembers = pickle.load(pkl_file)
      pkl_file.close()
      
   else:
      # Current and expired members going back to Jan 1 of the year prior to the rptYear.
      currentExpiredMembers = DbGet_CurrentExpiredMembers(cursor, rptYear)   # Returns a list sorted alphabetically
      
      pkl_file = open('cacheDb/currentExpiredMembers.pkl', 'wb')
      pickle.dump(currentExpiredMembers, pkl_file)
      pkl_file.close()
   #
   
   CurrentAndExpiredMembersReportAlphaSorted(currentExpiredMembers, rptYear)   # Done
   
   
   #----------------------------------------------------------------------------   
   #ExpiredMemberLabels()                                                # TODO
   #BoardMemberLabels()                                                  # TODO
   #RegionalCoordinatorLabels()                                          # TODO
   

   
   
   # Close database connection
   cursor.close()
   #db.commit()  Not writing to DB so don't commit()
   db.close()
   
   
   # Time the report generation
   elapsedTime = time.time() - startTime
   timeStruct = time.gmtime(elapsedTime)
   timeStr = time.strftime('%M:%S', timeStruct)
   print 'Elapsed Time = ', timeStr
   
   print "Finished All"
   sys.exit(0)


#
# EOF

