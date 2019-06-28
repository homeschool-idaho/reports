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
            msg = "ERROR -- Region is outside the range 1 - 19;  testing_history.testing_history_id = " +\
                str(a_testHist.testing_history_id)
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
         raise Exception("ERROR -- Missing member parent names. Member ID is " + str(nonmemberObj.member_id) )
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
         raise Exception("ERROR -- Missing member parent names. Member ID is " + str(nonmemberObj.member_id) )
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


def TestingReports(cursor, rptYear, regions):
   '''
   '''
   global date_time_stamp
   
   #-------------------------------------------------------------------
   # Testing Students By Region report
   #-------------------------------------------------------------------
   combinedDoc = Document()
   ss  = combinedDoc.StyleSheet
   
   ##pageNum = 0         # Starting page number is 1 -- will be pre-incremented
   ##totalNumPages = 1
   
   #pageNum = 0
   
   # Margins are top, left, bottom, right
   regRptMargins = MarginsPropertySet(top=1000, left=720, bottom=720, right=720) # bottom=720
   
   # Part of a Hack to fix page-numbering issue
   #bFirstRegion = True
   
   totalNumFamilies = 0
   totalNumTestingStudents = 0
   totalNumFamiliesByRegion = [0]*19
   totalNumStudentsByRegion = [0]*19
   
   totalFeesRecieved = 0
   totalMembershipFees = 0
   totalDonations = 0
   totalTestFees = 0
   totalMembershipRefunds = 0
   
   errorCt = 0
   
   print 'Type of regions: ', type(regions)   # DEBUG
   
   for region in regions:
      regionDoc = Document()
      
      # Create a new section for each region
      section = Section(paper=None, margins=regRptMargins, break_type=3, headery=None, footery=0, landscape=False) #, first_page_number=pageNum)
      combinedDoc.Sections.append( section )
      
      regionDoc.Sections.append( section )
      
      # Page Header and Footer
      #section.Header.append( r'{\pard \fs24 \tx%d\b %d ICHE Testing Students by Region / Parents \tab %d %s \par}' % 
      #                (Tab(5.5), testingReportYear, regionNum, regionName) )
      
      #section.Header.append( '%d ICHE Testing Students by Region / Parents         %s          %d %s' %
      #                                              (testingReportYear, todaysDate, regionNum, regionName) )
      #section.Footer.append( r'\fs16 \chdpa \tx%d \tab Page %d of %d' % (Tab(6), pageNum, totalNumPages) )
      
      #section.Footer.append( r'{\pard\ql\fs16 \chdpa\par} {\pard\qr\fs16 Page %d of %d\par}' % (pageNum, totalNumPages) )
      #section.Footer.append( r'{\pard\ql\fs16 \chdpa\par} {\pard\qr\fs16 \pgnstart%s\pgncont Page \chpgn\par}' % (pageNum) )
      #pageNum += 1
      '''
      if bFirstRegion:
         bFirstRegion = False
         section.Footer.append( r'\pgnstart%s\pgncont ' % (str(pageNum)) )
         section.Footer.append( r'{\pard\ql\fs16 \chdpa\par} {\pard\qr\fs16 Page \chpgn\par } ' )
      else:
         #pageNum += 1
         section.Footer.append( r'\pgnstart%s\pgncont ' % (str(pageNum)) )
         section.Footer.append( r'{\pard\ql\fs16 \chdpa\par} {\pard\qr\fs16 Page \chpgn\par } ' )
      #
      '''
      #section.Footer.append( r'\pgnstart%s\pgncont ' % (str(pageNum)) )
      #section.Footer.append( r'{\pard\qr\fs16 Page \chpgn\par } ')
      
      #section.Footer.append( r'{\pard\ql\fs16 \chdpa\par} ' )
      
      # For now, not using section.Header because it dims out the text like the footer. Using the following instead.
      p = Paragraph( ss.ParagraphStyles.Normal )
      #p.append( TEXT( r'{\pard \tx%d %d ICHE Testing Students by Region / Parents \tab %d %s \par}' % 
      #                (Tab(5.5), rptYear, region.regionNum, regionNames[region.regionNum - 1]), size=24, bold=True) )
      
      # ### Tabs not working here! ###
      p.append( TEXT( r'%d ICHE Testing Students by Region / Parents ' % (rptYear), size=24, bold=True) )
      
      p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
                
      p.append( TEXT( r'\tab   %d %s \line ' % (region.regionNum, regionNames[region.regionNum - 1]), size=24, bold=True) )
      section.append(p)
      
      #pageNum += 1
      
      #p = Paragraph( ss.ParagraphStyles.Normal )
      ##p.append( TEXT( r'Page %d' % (pageNum), size=16, bold=False) )
      #p.append( TEXT( r'\qc Page \chpgn', size=16, bold=False) )
      #p.append( TEXT( r'\pvpg\posyb\phpg\posxc\absw720') )
      #section.append(p)
      
      
      numFamilies = len(region.families)
         
      if numFamilies == 0:
         # Just print the page number and move on...
         
         p = Paragraph( ss.ParagraphStyles.Normal )
         p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
         section.append(p)
         
         try:
            os.mkdir('./output/')
         except:
            pass
         #
         try:
            os.mkdir('./output/TestingStudentsByRegionParents')
         except:
            pass
         #
         
         filename = './output/TestingStudentsByRegionParents/TestingStudentsByParentForRegion%d_' % (region.regionNum)
         filename += date_time_stamp + '.rtf'
      
         # Render and print the RTF
         DR = Renderer()                                           # From PyRTF
         DR.Write( regionDoc, file( filename, 'w' ) )
      
         continue
      #
      
      familyPerPageCount = 0
      familyNum = 0
      
      for family in region.families:
         familyNum += 1
         totalNumFamilies += 1
         totalNumFamiliesByRegion[region.regionNum - 1] += 1
         
         section.append('_' * 85)
         
         # Families
         p = Paragraph( ss.ParagraphStyles.Normal )
         p.append(r'\tx%d \tx%d \tx%d \tx%d \tx%d' % (Tab(.25), Tab(2.5), Tab(5.85), Tab(6.6), Tab(6.9) ) )
         
         #p.append( TEXT(r'\b %s, %s \b0\tab %s \tab %s \line' % 
         #               (family.member.mother_l_name, family.member.mother_f_name, family.member.phone_home, family.mailOptions), size=20))
         ph = family.member.phone_home
         if ph.strip() == '':
            ph = family.member.phone_work
            if ph.strip() == '':
               ph = '____________________'
            else:
               ph += ' (Work)'
            #
         else:
            ph += ' (Home)'
         #
         
         if not '_' in ph:   
            phone = ph[0:3] + '-' + ph[3:6] + '-' + ph[6:]
         #
         
         email = family.member.email
         if email.strip() == '':
            email = '____________________'
         #
         
         #if  family.member.mother_f_name == 'Carolina':
         #   can_break_here = 1
         #
         
         p.append( TEXT(r'\b %s, %s \b0\tab Phone: %s \line' % 
                        (family.member.mother_l_name, family.member.mother_f_name, phone), size=20))
         p.append( TEXT(r'\tab %s \tab E-mail: %s \line' % (family.member.street, email), size=20) )
         
         # CHECK FOR MISSING test_type
         for testingStudent in family.testingStudents:
            a_testHist = testingStudent.testing_history
            if not a_testHist.test_type in ['ITED', 'ITBS']:
               msg = "ERROR -- Missing test_type for testing_history.testing_history_id = " +\
                               str(a_testHist.testing_history_id)
               Log(msg)
               errorCt += 1
               #raise Exception(msg )
            #
         #
         
         #   Look ahead to find proctor
         proctor = ""
         for testingStudent in family.testingStudents:
            a_testHist = testingStudent.testing_history
            proctor = a_testHist.proctor
            break
         #
         if proctor == "":
            proctor = '____________________'
         #
         
         bItedOnly = True
         for testingStudent in family.testingStudents:
            a_testHist =  testingStudent.testing_history
            if a_testHist.test_type != 'ITED':
               bItedOnly = False
               break
            #
         #
         if bItedOnly:
            proctor = '(ITED Only) ' + proctor
         #
         
         p.append( TEXT(r'\tab %s, %s %s \tab Proctor: %s \tab ' 
                        % (family.member.city, family.member.state, family.member.zip, proctor), size=20))
         p.append( TEXT(r'Membership:', size=16))
         
         dues = 0.0
         for payment in family.payments:
            if payment.item == "membership":
               dues += payment.amount
               
            elif payment.item.find('refund') != -1:
               dues -= payment.amount                    # Subtract refunds from dues -- so dues are adjuusted for refunds.
               totalMembershipRefunds += payment.amount
            #
         #
         p.append( TEXT(r'{\tqr\tab %05.2f}\line' % (dues), size=20) )
         donation = 0.0
         for payment in family.payments:
            if payment.item == "donation":
               donation += payment.amount
            #
         #
         #p.append( TEXT(r'\tql\tab \tab \tab Donation:', size=16) )
         p.append( TEXT(r'\tab \tab \tab Donation:', size=16) )
         p.append( TEXT(r'{\tqr\tab %05.2f}' % (donation), size=20) )
         section.append(p)
         
         # Students header
         p = Paragraph( ss.ParagraphStyles.Normal )
         p.append(r'\tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d' % 
                  (Tab(.25), Tab(2.5), Tab(2.85), Tab(3.65), Tab(4.1), Tab(4.55), Tab(4.95), Tab(5.4), Tab(5.85), Tab(6.6)) )
         p.append( 
            TEXT(r'\ulw \tab Students \tab Sex \tab Birthdate \tab Grade \tab Test \tab Level \tab Home \tab Public \tab Campus \tab Fee \line ',
                 size=16 ) )
         
         # Students
         total_test_fees = 0
         for testingStudent in family.testingStudents:
            totalNumTestingStudents += 1
            totalNumStudentsByRegion[region.regionNum - 1] += 1
            
            a_student = testingStudent.student
            a_testHist = testingStudent.testing_history
            
            p.append(r'\tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d' % 
                     (Tab(.25), Tab(2.5), Tab(2.85), Tab(3.7), Tab(4.1), Tab(4.55), Tab(4.95), Tab(5.4), Tab(5.85), Tab(6.6)) )
            
            if a_testHist.returning == 'y':
               test_fee = 29.00
            else:
               test_fee = 34.00
            
            total_test_fees += test_fee
            
            # CHECK FOR BAD DATA!
            if not a_testHist.campus in ['N', 'E', 'W', 'S']:
               a_testHist.campus = '-'
               msg = "ERROR -- Campus is not one of 'N', 'E', 'W', 'S' for testing_history.testing_history_id " +\
                     str(a_testHist.testing_history_id)
               #raise Exception("ERROR -- Campus is not one of 'N', 'E', 'W', 'S' for testing_history.testing_history_id " +\
               #      a_testHist.testing_history_id + ". Fix this before proceeding.")
               print msg
               Log(msg)
               errorCt += 1
            #
            
            if (a_testHist.grade < 9 and a_testHist.test_type == 'ITED'):
               msg = 'ERROR - test type should be ITBS for grade %d for testing_history.testing_history_id %d' %\
                   (a_testHist.grade, a_testHist.testing_history_id)
               print msg
               Log(msg)
               errorCt += 1
            #
            if (a_testHist.grade > 9 and a_testHist.test_type == 'ITBS'):
               msg = 'ERROR - test type should be ITED for grade %d for testing_history.testing_history_id %d' %\
                   (a_testHist.grade, a_testHist.testing_history_id)
               print msg
               Log(msg)
               errorCt += 1
            #
            
            text = TEXT(r' \tab %s, %s \tab %s \tab %s \tab %d \tab %s \tab %d \tab %d \tab %d \tab %s \tab %05.2f\line' %
                    (a_student.l_name, a_student.f_name, a_student.gender, a_student.dob, a_testHist.grade, a_testHist.test_type, 
                     a_testHist.level, a_testHist.years_hs, a_testHist.years_ps, a_testHist.campus, test_fee), size=20 )
            print 'text = ', text.Data
            p.append( text )
            
            #p.append( 
            #   TEXT(r' \tab %s, %s \tab %s \tab %s \tab %d \tab %s \tab %d \tab %d \tab %d \tab %s \tab %s\line' %
            #        (a_student.l_name, a_student.f_name, a_student.gender, a_student.dob, a_testHist.grade, a_testHist.test_type, 
            #         a_testHist.level, a_testHist.years_hs, a_testHist.years_ps, a_testHist.campus, test_fee), size=20 ) )
            
         # End for student in testingStudents
         section.append(p)
         
         # Family payment totals
         totalPayment = total_test_fees + dues + donation
         
         totalFeesRecieved += totalPayment
         totalMembershipFees += dues
         totalDonations += donation
         totalTestFees += total_test_fees
         
         p = Paragraph( ss.ParagraphStyles.Normal )
         p.append(r'\tx%d \tx%d \tx%d' % ( Tab(5.85), Tab(6.52), Tab(6.6) ) )
         
         p.append( TEXT(r'\tab Testing:', size=16))
         if total_test_fees >= 100:
            p.append( TEXT(r'{\tqr\tab %05.2f}\line' % (total_test_fees), size=20) )
         else:
            p.append( TEXT(r'{\tqr\tab\tab %05.2f}\line' % (total_test_fees), size=20) )
         #
         #p.append( TEXT(r'\tql\tab\b Total:\b0', size=16) )
         p.append( TEXT(r'\tab\b Total:\b0', size=16) )
         if totalPayment >= 100:
            p.append( TEXT(r'{\tqr\tab\b %05.2f\b0} ' % (totalPayment), size=20) )
         else:
            p.append( TEXT(r'{\tqr\tab\tab\b %05.2f\b0} ' % (totalPayment), size=20) )
         #
         section.append(p)
         
         
         # Limit 4 families per page so we don't have page breaks in the middle of a family.
         familyPerPageCount += 1
         
         bPrintPageNum = False
         #bAtPageEnd = False
         bAddPageBreak = False
         
         if familyPerPageCount == 4:   # is per region
            familyPerPageCount = 0
            
            if familyNum != numFamilies:
               #pageNum += 1
               #p.append( TEXT(r'\page') )
               bPrintPageNum = True
               #bAtPageEnd = True
               bAddPageBreak = True
               
            elif familyNum == numFamilies:
               #pageNum += 1
               # New section will insert a page break
               bPrintPageNum = True
               #bAtPageEnd = True
               #bAddPageBreak = False
               #
            
         elif familyPerPageCount in [2,3]:
            if familyNum != numFamilies:
               # Don't incr pageNum
               # Don't append \page
               # Don't print page number
               # Not at page end yet
               pass
            
            elif familyNum == numFamilies:
               #pageNum += 1
               # New section will insert a page break
               bPrintPageNum = True
               #bAtPageEnd = True
            #
            
         elif familyPerPageCount == 1:
            if familyNum != numFamilies:
               # Don't incr pageNum
               # Don't append \page
               # Don't print page number
               # Not at page end yet
               pass
            
            elif familyNum == numFamilies:
               #pageNum += 1
               # New section will insert a page break
               bPrintPageNum = True
               #bAtPageEnd = True
            #
         #
         
         
         #if bPrintPageNum and bAtPageEnd:
         if bPrintPageNum:
            p = Paragraph( ss.ParagraphStyles.Normal )
            
            #p.append( TEXT( r'Page %d' % (pageNum), size = 16, bold = False) )
            #p.append( TEXT( r'\pvmrg\posyb\phpg\posxc\absw720') )
            #p.append( TEXT( r'\qc Page \chpgn', size = 16, bold = False) )
            
            p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')   # absw720
            
            section.append(p)
         #
         
         if bAddPageBreak:
            #p.append(r'\page')
            section.append(r'\page')
            
            # Print title on each page
            p = Paragraph( ss.ParagraphStyles.Normal )
            p.append( TEXT( r'%d ICHE Testing Students by Region / Parents ' % (rptYear), size=24, bold=True) )
            p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
            p.append( TEXT( r'\tab   %d %s \line ' % (region.regionNum, regionNames[region.regionNum - 1]), size=24, bold=True) )
            section.append(p)
         #
         
      # End for families in region
      
      try:
         os.mkdir('./output/')
      except:
         pass
      #
      try:
         os.mkdir('./output/TestingStudentsByRegionParents')
      except:
         pass
      #
      
      filename = './output/TestingStudentsByRegionParents/TestingStudentsByParentForRegion%d_' % (region.regionNum)
      filename += date_time_stamp + '.rtf'
   
      # Render and print the RTF
      DR = Renderer()                                           # From PyRTF
      DR.Write( regionDoc, file( filename, 'w' ) )
      
   # End for region in regions
   
   
   # Summary Page -- lets have some sanity!
   section = Section(paper=None, margins=regRptMargins, break_type=3, headery=None, footery=0, 
                     landscape=False) #, first_page_number=pageNum)
   combinedDoc.Sections.append( section )
   p = Paragraph( ss.ParagraphStyles.Normal )
   
   # ### Tabs not working here! ###
   p.append( TEXT( r'Summary: %d Testing Students By Region / Parents ' % (rptYear), size=24, bold=True) )
   p.append( TEXT( r'{\pard \tx%d \tab     %s \line \line \par}' % (Tab(4.6), date_stamp), size=16, bold=False) )
   
   p.append( TEXT( r'{\pard \tx%d \tx%d \ulw Region \tab Families \tab Students \ul0\par} \line ' %\
                   ( Tab(1.9), Tab(2.8)), size=20, bold=True ) )
   
   for regionNum in range(1, 20):
      p.append( TEXT( r'{\pard \tx%d \tx%d %2d %s: \tab %d \tab %d \par } '
                      % ( Tab(1.9), Tab(2.8), regionNum, regionNames[regionNum - 1], 
                         totalNumFamiliesByRegion[regionNum - 1], totalNumStudentsByRegion[regionNum - 1]),
                         size=20, bold=False) )
   #
   
   p.append( TEXT( r'\line {\pard\tx%d \tx%d \b Statewide Totals: \b0\tab %d \tab %d \line\par} '
                   % (Tab(1.9), Tab(2.8), totalNumFamilies, totalNumTestingStudents), size=20, bold=False) )
   
   section.append(p)
   
   p = Paragraph( ss.ParagraphStyles.Normal )
   p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
   section.append(p)
   
   
   # Get Date-time stamp
   #t = time.localtime()
   #date_time_stamp = str(t[0]) + '-%02d' % t[1] + '-%02d' % t[2] + '_%02d' % t[3] + '-%02d' % t[4]
   filename = './output/TestingStudentsByRegionParents_' + date_time_stamp + '.rtf'
   
   # Render and print the RTF
   DR = Renderer()                                           # From PyRTF
   DR.Write( combinedDoc, file( filename, 'w' ) )
   
   
   #----------------------------------------------------------------------------
   # Finance Report
   #----------------------------------------------------------------------------
   
   doc = Document()
   
   # Margins are top, left, bottom, right
   regRptMargins = MarginsPropertySet(top=1000, left=720, bottom=720, right=720)
   
   
   # Create a new section for each region
   section = Section(paper=None, margins=regRptMargins, break_type=3, headery=None, footery=0,
                     landscape=False) #, first_page_number=pageNum)
   doc.Sections.append( section )
   
   ss  = doc.StyleSheet
   p = Paragraph( ss.ParagraphStyles.Normal )
   
   # Totaling membership dues and test fees from Jan 1st of the year prior to the year in which testing occurs.
   paymentStartDate = '-'.join( [str(rptYear-1), '01', '01'])
   
   msg1 = r'{\b\fs24ICHE Testing Families Finance Report -- Since %s }\line\line' % (paymentStartDate)
   
   msg2 = r'\pard\fs20\tqr\tx%d Total Membership: \tab %.2f \par' % (Tab(2), totalMembershipFees)
   msg3 = r'\pard\fs20\tqr\tx%d Total Donations: \tab %.2f \par' % (Tab(2), totalDonations)
   msg4 = r'\pard\fs20\tqr\tx%d Total Test Fees: \tab %.2f \par' % (Tab(2), totalTestFees)
   msg41=                r'--------------------------------------------\line'
   msg5 = r'{\pard\fs20\b\tqr\tx%d Subtotal Recieved: \tab %.2f \line\par}' % (Tab(2), totalFeesRecieved)
   
   msg6 = r'\pard\fs20\tqr\tx%d\tq\tx%d Total Refunds: \tab <%.2f> \tab (Membership Refunds for testing families)\par' %\
                                                                   (Tab(2), Tab(2.2), totalMembershipRefunds)
   #msg6 = r'{\pard\fs20\tqr\tx%d Total Refunds: \tab %.2f  (Membership Refunds for testing families) \par}' % (Tab(2), totalMembershipRefunds )
   
   msg61=                r'--------------------------------------------\line'
   msg7 = r'{\pard\fs20\b\tqr\tx%d Total Received: \tab %.2f \par}' % (Tab(2), totalFeesRecieved - totalMembershipRefunds)
   
   msg8 = r'\line\line\fs20 The above amounts DO NOT include non-testing family memberships, donations or refunds. \line'
   
   bIncludeFees = True
   if bIncludeFees:
      p = Paragraph( ss.ParagraphStyles.Normal )
      p.append( msg1)
      p.append( msg2)
      p.append( msg3)
      p.append( msg4)
      p.append( msg41)
      p.append( msg5)
      p.append( msg6)
      p.append( msg61)
      p.append( msg7)
      p.append( msg8)
      
      '''
      p.append( TEXT( msg1, size=24, bold=True ))
      p.append( TEXT( msg2, size=20, bold=False ))
      p.append( TEXT( msg3, size=20, bold=False ))
      p.append( TEXT( msg4, size=20, bold=False ))
      p.append( TEXT( msg41,size=20, bold=False ))
      p.append( TEXT( msg5, size=20, bold=True ))
      p.append( TEXT( msg6, size=20, bold=False ))
      p.append( TEXT( msg61,size=20, bold=False ))
      p.append( TEXT( msg7, size=20, bold=True ))
      p.append( TEXT( msg8, size=20, bold=False ))
      '''
      section.append(p)
   #
   
   if 0:
      print msg1   # DEBUG
      print msg2
      print msg3
      print msg4
      print msg5
      print msg6
      print msg7
   #
   
   filename = './output/TestingStudentsFinanceReport_' + date_time_stamp + '.rtf'
   
   # Render and print the RTF
   DR = Renderer()                                           # From PyRTF
   DR.Write( doc, file( filename, 'w' ) )
   
   #----------------------------------------------------------------------------
   # Final error count
   #
   print 'Error count =', errorCt
   
# End TestingReports()


def TestingReports_Ited_Regions4and5_Only(cursor, rptYear, testingRegions):
   '''
   '''
   global date_time_stamp
   
   #-------------------------------------------------------------------
   # Testing Students By Region report
   #-------------------------------------------------------------------
   combinedDoc = Document()
   ss  = combinedDoc.StyleSheet
   
   # Margins are top, left, bottom, right
   regRptMargins = MarginsPropertySet(top=1000, left=720, bottom=720, right=720) # bottom=720
   
   totalNumFamilies = 0
   totalNumTestingStudents = 0
   totalNumFamiliesByRegion = [0]*19
   totalNumStudentsByRegion = [0]*19
   
   totalFeesRecieved = 0
   totalMembershipFees = 0
   totalDonations = 0
   totalTestFees = 0
   totalMembershipRefunds = 0
   
   errorCt = 0
   
   for region in testingRegions:
      if not region.regionNum in [4, 5]:
         continue
      #
      
      #regionDoc = Document()
      
      # Create a new section for each region
      section = Section(paper=None, margins=regRptMargins, break_type=3, headery=None, footery=0, landscape=False) #, first_page_number=pageNum)
      combinedDoc.Sections.append( section )
      
      #regionDoc.Sections.append( section )
      
      # For now, not using section.Header because it dims out the text like the footer. Using the following instead.
      p = Paragraph( ss.ParagraphStyles.Normal )
      
      # ### Tabs not working here! ###
      p.append( TEXT( r'%d ICHE ITED-Only Parents ' % (rptYear), size=24, bold=True) )
      p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
      p.append( TEXT( r'\tab   %d %s \line ' % (region.regionNum, regionNames[region.regionNum - 1]), size=24, bold=True) )
      section.append(p)
      
      numFamilies = len(region.families)
      
      if numFamilies == 0:
         # Just print the page number and move on...
         
         p = Paragraph( ss.ParagraphStyles.Normal )
         p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
         section.append(p)
         
         '''
         try:
            os.mkdir('./output/')
         except:
            pass
         #
         try:
            os.mkdir('./output/TestingStudentsByRegionParents')
         except:
            pass
         #
         
         filename = './output/TestingStudentsByRegionParents/TestingStudentsByParentForRegion%d_' % (region.regionNum)
         filename += date_time_stamp + '.rtf'
         
         # Render and print the RTF
         DR = Renderer()                                           # From PyRTF
         DR.Write( regionDoc, file( filename, 'w' ) )
         '''
         
         continue
      #
      
      # Get count of ITED-Only families in this region
      numItedOnlyFamilies = 0   # In this region
      for family in region.families:
         
         # CHECK FOR ITED ONLY
         bHasItbs = False
         for testingStudent in family.testingStudents:
            a_testHist = testingStudent.testing_history
            if a_testHist.test_type == 'ITBS':
               bHasItbs = True
               break
            #
         #
         if bHasItbs:
            continue
         #
         numItedOnlyFamilies += 1
      #
      
      familyPerPageCount = 0
      familyNum = 0
      
      for family in region.families:
         
         # CHECK FOR ITED ONLY
         bHasItbs = False
         for testingStudent in family.testingStudents:
            a_testHist = testingStudent.testing_history
            if a_testHist.test_type == 'ITBS':
               bHasItbs = True
               break
            #
         #
         if bHasItbs:
            continue
         #
         
         # NOW HAVE ITED ONLY
         familyNum += 1
         totalNumFamilies += 1
         totalNumFamiliesByRegion[region.regionNum - 1] += 1
         
         section.append('_' * 85)
         
         # Families
         p = Paragraph( ss.ParagraphStyles.Normal )
         p.append(r'\tx%d \tx%d \tx%d \tx%d \tx%d' % (Tab(.25), Tab(2.5), Tab(5.85), Tab(6.6), Tab(6.9) ) )
         
         ph = family.member.phone_home
         if ph.strip() == '':
            ph = family.member.phone_work
            if ph.strip() == '':
               ph = '____________________'
            else:
               ph += ' (Work)'
            #
         else:
            ph += ' (Home)'
         #
         
         if not '_' in ph:   
            phone = ph[0:3] + '-' + ph[3:6] + '-' + ph[6:]
         #
         
         email = family.member.email
         if email.strip() == '':
            email = '____________________'
         #
         
         p.append( TEXT(r'\b %s, %s \b0\tab Phone: %s \line' % 
                        (family.member.mother_l_name, family.member.mother_f_name, phone), size=20))
         p.append( TEXT(r'\tab %s \tab E-mail: %s \line' % (family.member.street, email), size=20) )
         
         # CHECK FOR MISSING test_type
         for testingStudent in family.testingStudents:
            a_testHist = testingStudent.testing_history
            if not a_testHist.test_type in ['ITED', 'ITBS']:
               msg = "ERROR -- Missing test_type for testing_history.testing_history_id = " +\
                               str(a_testHist.testing_history_id)
               Log(msg)
               errorCt += 1
               #raise Exception(msg )
            #
         #
         
         #   Look ahead to find proctor
         proctor = ""
         for testingStudent in family.testingStudents:
            a_testHist = testingStudent.testing_history
            proctor = a_testHist.proctor
            break
         #
         if proctor == "":
            proctor = '____________________'
         #
         
         bItedOnly = True
         for testingStudent in family.testingStudents:
            a_testHist =  testingStudent.testing_history
            if a_testHist.test_type != 'ITED':
               bItedOnly = False
               break
            #
         #
         if bItedOnly:
            proctor = '(ITED Only) ' + proctor
         #
         
         p.append( TEXT(r'\tab %s, %s %s \tab Proctor: %s \tab ' 
                        % (family.member.city, family.member.state, family.member.zip, proctor), size=20))
         p.append( TEXT(r'Membership:', size=16))
         
         dues = 0.0
         for payment in family.payments:
            if payment.item == "membership":
               dues += payment.amount
               
            elif payment.item.find('refund') != -1:
               dues -= payment.amount                    # Subtract refunds from dues -- so dues are adjuusted for refunds.
               totalMembershipRefunds += payment.amount
            #
         #
         p.append( TEXT(r'{\tqr\tab %05.2f}\line' % (dues), size=20) )
         donation = 0.0
         for payment in family.payments:
            if payment.item == "donation":
               donation += payment.amount
            #
         #
         #p.append( TEXT(r'\tql\tab \tab \tab Donation:', size=16) )
         p.append( TEXT(r'\tab \tab \tab Donation:', size=16) )
         p.append( TEXT(r'{\tqr\tab %05.2f}' % (donation), size=20) )
         section.append(p)
         
         # Students header
         p = Paragraph( ss.ParagraphStyles.Normal )
         p.append(r'\tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d' % 
                  (Tab(.25), Tab(2.5), Tab(2.85), Tab(3.65), Tab(4.1), Tab(4.55), Tab(4.95), Tab(5.4), Tab(5.85), Tab(6.6)) )
         p.append( 
            TEXT(r'\ulw \tab Students \tab Sex \tab Birthdate \tab Grade \tab Test \tab Level \tab Home \tab Public \tab Campus \tab Fee \line ',
                 size=16 ) )
         
         # Students
         total_test_fees = 0
         for testingStudent in family.testingStudents:
            totalNumTestingStudents += 1
            totalNumStudentsByRegion[region.regionNum - 1] += 1
            
            a_student = testingStudent.student
            a_testHist = testingStudent.testing_history
            
            p.append(r'\tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d' % 
                     (Tab(.25), Tab(2.5), Tab(2.85), Tab(3.7), Tab(4.1), Tab(4.55), Tab(4.95), Tab(5.4), Tab(5.85), Tab(6.6)) )
            
            if a_testHist.returning == 'y':
               test_fee = 29.00
            else:
               test_fee = 34.00
            
            total_test_fees += test_fee
            
            # CHECK FOR BAD DATA!
            if not a_testHist.campus in ['N', 'E', 'W', 'S']:
               a_testHist.campus = '-'
               msg = "ERROR -- Campus is not one of 'N', 'E', 'W', 'S' for testing_history.testing_history_id " +\
                     str(a_testHist.testing_history_id)
               #raise Exception("ERROR -- Campus is not one of 'N', 'E', 'W', 'S' for testing_history.testing_history_id " +\
               #      a_testHist.testing_history_id + ". Fix this before proceeding.")
               print msg
               Log(msg)
               errorCt += 1
            #
            
            if (a_testHist.grade < 9 and a_testHist.test_type == 'ITED'):
               msg = 'ERROR - test type should be ITBS for grade %d for testing_history.testing_history_id %d' %\
                   (a_testHist.grade, a_testHist.testing_history_id)
               print msg
               Log(msg)
               errorCt += 1
            #
            if (a_testHist.grade > 9 and a_testHist.test_type == 'ITBS'):
               msg = 'ERROR - test type should be ITED for grade %d for testing_history.testing_history_id %d' %\
                   (a_testHist.grade, a_testHist.testing_history_id)
               print msg
               Log(msg)
               errorCt += 1
            #
            
            text = TEXT(r' \tab %s, %s \tab %s \tab %s \tab %d \tab %s \tab %d \tab %d \tab %d \tab %s \tab %05.2f\line' %
                    (a_student.l_name, a_student.f_name, a_student.gender, a_student.dob, a_testHist.grade, a_testHist.test_type, 
                     a_testHist.level, a_testHist.years_hs, a_testHist.years_ps, a_testHist.campus, test_fee), size=20 )
            print 'text = ', text.Data
            p.append( text )
            
         # End for student in testingStudents
         section.append(p)
         
         # Family payment totals
         totalPayment = total_test_fees + dues + donation
         
         totalFeesRecieved += totalPayment
         totalMembershipFees += dues
         totalDonations += donation
         totalTestFees += total_test_fees
         
         p = Paragraph( ss.ParagraphStyles.Normal )
         p.append(r'\tx%d \tx%d \tx%d' % ( Tab(5.85), Tab(6.52), Tab(6.6) ) )
         
         p.append( TEXT(r'\tab Testing:', size=16))
         if total_test_fees >= 100:
            p.append( TEXT(r'{\tqr\tab %05.2f}\line' % (total_test_fees), size=20) )
         else:
            p.append( TEXT(r'{\tqr\tab\tab %05.2f}\line' % (total_test_fees), size=20) )
         #
         #p.append( TEXT(r'\tql\tab\b Total:\b0', size=16) )
         p.append( TEXT(r'\tab\b Total:\b0', size=16) )
         if totalPayment >= 100:
            p.append( TEXT(r'{\tqr\tab\b %05.2f\b0} ' % (totalPayment), size=20) )
         else:
            p.append( TEXT(r'{\tqr\tab\tab\b %05.2f\b0} ' % (totalPayment), size=20) )
         #
         section.append(p)
         
         
         # Limit 4 families per page so we don't have page breaks in the middle of a family.
         familyPerPageCount += 1
         
         bPrintPageNum = False
         #bAtPageEnd = False
         bAddPageBreak = False
         
         if familyPerPageCount == 4:   # is per region
            familyPerPageCount = 0
            
            #if familyNum != numFamilies:
            if familyNum != numItedOnlyFamilies:
               #pageNum += 1
               #p.append( TEXT(r'\page') )
               bPrintPageNum = True
               #bAtPageEnd = True
               bAddPageBreak = True
               
            #elif familyNum == numFamilies:
            elif familyNum == numItedOnlyFamilies:
               #pageNum += 1
               # New section will insert a page break
               bPrintPageNum = True
               #bAtPageEnd = True
               #bAddPageBreak = False
               #
            
         elif familyPerPageCount in [2,3]:
            #if familyNum != numFamilies:
            if familyNum != numItedOnlyFamilies:
               # Don't incr pageNum
               # Don't append \page
               # Don't print page number
               # Not at page end yet
               pass
            
            #elif familyNum == numFamilies:
            elif familyNum == numItedOnlyFamilies:
               #pageNum += 1
               # New section will insert a page break
               bPrintPageNum = True
               #bAtPageEnd = True
            #
            
         elif familyPerPageCount == 1:
            #if familyNum != numFamilies:
            if familyNum != numItedOnlyFamilies:
               # Don't incr pageNum
               # Don't append \page
               # Don't print page number
               # Not at page end yet
               pass
            
            #elif familyNum == numFamilies:
            elif familyNum == numItedOnlyFamilies:
               #pageNum += 1
               # New section will insert a page break
               bPrintPageNum = True
               #bAtPageEnd = True
            #
         #
         
         
         #if bPrintPageNum and bAtPageEnd:
         if bPrintPageNum:
            p = Paragraph( ss.ParagraphStyles.Normal )
            p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')   # absw720
            section.append(p)
         #
         
         if bAddPageBreak:
            section.append(r'\page')
            
            p = Paragraph( ss.ParagraphStyles.Normal )
            p.append( TEXT( r'%d ICHE ITED-Only Parents ' % (rptYear), size=24, bold=True) )
            p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
            p.append( TEXT( r'\tab   %d %s \line ' % (region.regionNum, regionNames[region.regionNum - 1]), size=24, bold=True) )
            section.append(p)            
         #
         
      # End for families in region
      
      '''
      try:
         os.mkdir('./output/')
      except:
         pass
      #
      try:
         os.mkdir('./output/TestingStudentsByRegionParents')
      except:
         pass
      #
      
      # filename = './output/TestingStudentsByRegionParents/TestingStudentsByParentForRegion%d_' % (region.regionNum)
      # filename += date_time_stamp + '.rtf'
      
      # Render and print the RTF
      DR = Renderer()                                           # From PyRTF
      DR.Write( regionDoc, file( filename, 'w' ) )
      '''
      
   # End for region in regions
   
   '''
   # Summary Page -- lets have some sanity!
   section = Section(paper=None, margins=regRptMargins, break_type=3, headery=None, footery=0, 
                     landscape=False) #, first_page_number=pageNum)
   combinedDoc.Sections.append( section )
   p = Paragraph( ss.ParagraphStyles.Normal )
   
   # ### Tabs not working here! ###
   p.append( TEXT( r'Summary: %d Testing Students By Region / Parents ' % (rptYear), size=24, bold=True) )
   p.append( TEXT( r'{\pard \tx%d \tab     %s \line \line \par}' % (Tab(4.6), date_stamp), size=16, bold=False) )
   
   p.append( TEXT( r'{\pard \tx%d \tx%d \ulw Region \tab Families \tab Students \ul0\par} \line ' %\
                   ( Tab(1.9), Tab(2.8)), size=20, bold=True ) )
   
   for regionNum in range(1, 20):
      p.append( TEXT( r'{\pard \tx%d \tx%d %2d %s: \tab %d \tab %d \par } '
                      % ( Tab(1.9), Tab(2.8), regionNum, regionNames[regionNum - 1], 
                         totalNumFamiliesByRegion[regionNum - 1], totalNumStudentsByRegion[regionNum - 1]),
                         size=20, bold=False) )
   #
   
   p.append( TEXT( r'\line {\pard\tx%d \tx%d \b Statewide Totals: \b0\tab %d \tab %d \line\par} '
                   % (Tab(1.9), Tab(2.8), totalNumFamilies, totalNumTestingStudents), size=20, bold=False) )
   
   section.append(p)
   
   p = Paragraph( ss.ParagraphStyles.Normal )
   p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
   section.append(p)
   '''
   
   # Get Date-time stamp
   #t = time.localtime()
   #date_time_stamp = str(t[0]) + '-%02d' % t[1] + '-%02d' % t[2] + '_%02d' % t[3] + '-%02d' % t[4]
   filename = './output/TestingItedOnlyParents_' + date_time_stamp + '.rtf'
   
   # Render and print the RTF
   DR = Renderer()                                           # From PyRTF
   DR.Write( combinedDoc, file( filename, 'w' ) )
   
   #----------------------------------------------------------------------------
   # Final error count
   #
   print 'ITED-Only error count =', errorCt
   
# End TestingReport_Ited_Regions4and5Only()


def TestCountReports(cursor, rptYear, regions, bNewRet=False):
   '''
   Two reports; one has new and returning student counts; the other does not.
   '''
   #----------------------------------------------------------------------------
   # Test Count By Region Report
   #----------------------------------------------------------------------------
   
   #-------------------
   # Accumulate totals
   #-------------------
   errorCt = 0
   
   # By Region
   newItbsStudents   = [0] * 19;   newItedStudents          = [0] * 19
   newGrade9Students = [0] * 19;   newGrades_11_12_students = [0] * 19;   newLevel14Students = [0] * 19
   
   retItbsStudents   = [0] * 19;   retItedStudents          = [0] * 19
   retGrade9Students = [0] * 19;   retGrades_11_12_students = [0] * 19;   retLevel14Students = [0] * 19
   
   totItbsStudents   = [0] * 19;   totItedStudents          = [0] * 19
   totGrade9Students = [0] * 19;   totGrades_11_12_students = [0] * 19;   totLevel14Students = [0] * 19
   
   itbsFamilies      = [0] * 19;   itedFamilies             = [0] * 19
   itbsOnlyFamilies  = [0] * 19;   itedOnlyFamilies         = [0] * 19
   
   itbsLevelCounts   = [{}] * 19   #   Example: itbsLevelCounts[1]['9-3-new'] += 1
   itedLevelCounts   = [{}] * 19
   
   totalFamilies     = [0] * 19
   
   regionNum = -1
   for region in regions:
      regionNum += 1
      itbsLevelCounts[regionNum] = {}
      itedLevelCounts[regionNum] = {}
      
      for family in region.families:
         totalFamilies[regionNum] += 1
         
         bHasItbs = False
         bHasIted = False
         
         for testingStudent in family.testingStudents:
            a_testHist = testingStudent.testing_history
            
            '''
            # DEBUG below
            a_student = testingStudent.student
            
            if regionNum == 12 and a_testHist.level == 16:
               print '#########', a_student.f_name, a_student.l_name
            #
            # DEBUG Above
            '''
            
            #TESTING_HISTORY_COL_NAMES =  ('testing_history_id', 'student_id', 'payment_id', 'grade', 'level',
            #                  'campus', 'test_type', 'region', 'test_year', 'years_hs', 'years_ps',
            #                  'returning', 'self.proctor', 'canceled', 'summa', 'dual', 'whos_who',
            #                  'date_entered', 'date_modified', 'comment')
            
            bNew = False
            if a_testHist.returning == 'y':
               key = '-'.join([str(a_testHist.level), str(a_testHist.grade), 'ret'])
            else:
               key = '-'.join([str(a_testHist.level), str(a_testHist.grade), 'new'])
               bNew = True
            #
            totKey = '-'.join([str(a_testHist.level), str(a_testHist.grade), 'tot'])
            
            if a_testHist.test_type == 'ITBS':
               bHasItbs = True
               
               if key in itbsLevelCounts[regionNum].keys():
                  itbsLevelCounts[regionNum][key] += 1
               else:
                  itbsLevelCounts[regionNum][key] = 1
               #
               
               if totKey in itbsLevelCounts[regionNum].keys():
                  itbsLevelCounts[regionNum][totKey] += 1
               else:
                  itbsLevelCounts[regionNum][totKey] = 1
               #
               
               if bNew:
                  newItbsStudents[regionNum] += 1
               else:
                  retItbsStudents[regionNum] += 1
               #
               
               totItbsStudents[regionNum] += 1
               
            elif a_testHist.test_type == 'ITED':
               bHasIted = True
               
               if key in itedLevelCounts[regionNum].keys():
                  itedLevelCounts[regionNum][key] += 1
               else:
                  itedLevelCounts[regionNum][key] = 1
               #
               
               if totKey in itedLevelCounts[regionNum].keys():
                  itedLevelCounts[regionNum][totKey] += 1
               else:
                  itedLevelCounts[regionNum][totKey] = 1
               #
               
               if bNew:
                  newItedStudents[regionNum] += 1
               else:
                  retItedStudents[regionNum] += 1
               #
               
               totItedStudents[regionNum] += 1
               
            else:
               msg = 'ERROR -- Illegal test type ' + a_testHist.test_type +\
                   'for testing_history.testing_history_id: ' + str(a_testHist.testing_history_id)
               Log(msg)
               errorCt += 1
               #raise Exception(msg)
            #
            
            if a_testHist.level == 14:
               if bNew:
                  newLevel14Students[regionNum] += 1
               else:
                  retLevel14Students[regionNum] += 1
               #
               
               totLevel14Students[regionNum] += 1
            #
            
            if a_testHist.grade == 9:
               if bNew:
                  newGrade9Students[regionNum] += 1
               else:
                  retGrade9Students[regionNum] += 1
               #
               
               totGrade9Students[regionNum] += 1
            #
            
            if a_testHist.grade == 11 or a_testHist.grade == 12:
               if bNew:
                  newGrades_11_12_students[regionNum] += 1
               else:
                  retGrades_11_12_students[regionNum] += 1
               #
               
               totGrades_11_12_students[regionNum] += 1
            #
            
         #  For student
         
         if bHasItbs:
            itbsFamilies[regionNum] += 1
            if not bHasIted:
               itbsOnlyFamilies[regionNum] += 1
            #
         #
         if bHasIted:
            itedFamilies[regionNum] += 1
            if not bHasItbs:
               itedOnlyFamilies[regionNum] += 1
            #
         #
         
      #  For family
      
   # for regionNum
   
   #------------------
   # Write the report
   #------------------
   doc = Document()
   
   # Margins are top, left, bottom, right
   regRptMargins = MarginsPropertySet(top=1000, left=720, bottom=720, right=720)
   
   regionNum = -1
   for region in regions:
      regionNum += 1
      
      # Create a new section for each region
      section = Section(paper=None, margins=regRptMargins, break_type=3, headery=None, footery=0, landscape=False) #, first_page_number=pageNum)
      doc.Sections.append( section )
      
      ss  = doc.StyleSheet
      p = Paragraph( ss.ParagraphStyles.Normal )
      
      # Page title
      p.append( TEXT( r'%d ICHE Test Count by Region ' % (rptYear), size=24, bold=True) )
      
      p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
                
      p.append( TEXT( r'\tab   %d %s \line ' % (region.regionNum, regionNames[region.regionNum - 1]), size=24, bold=True) )
      section.append(p)
      
      #---------------------------
      # ITBS
      #---------------------------
      p = Paragraph( ss.ParagraphStyles.Normal )
        
      p.append(r'______________________________________________________________\line ITBS \line\line')
      if bNewRet:
         p.append(r'\tx%d \tx%d \tx%d \tx%d \tx%d ' % (Tab(1.5), Tab(2.1), Tab(2.8), Tab(3.25), Tab(4) ) )
         p.append( TEXT(r'\ulw\tab Level \tab Grade \tab New \tab Returning \tab Total', size=20, bold=False) )
      else:
         p.append(r'\tx%d \tx%d \tx%d ' % (Tab(1.5), Tab(2.1), Tab(2.8) ) )
         p.append( TEXT(r'\ulw\tab Level \tab Grade \tab Total', size=20, bold=False) )
      #
      section.append(p)
      
      p = Paragraph( ss.ParagraphStyles.Normal )
      
      newAccm = retAccm = totAccm = 0
      
      for grade in range(3, 10):   # 3-9 inclusive
         if grade == 9:
            level = 14
         else:
            level = grade + 6
         #
         
         if bNewRet:
            p.append(r'{\pard\sl317\tqr\tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d ' % (Tab(1.75), Tab(2.35), Tab(3.08), Tab(3.65), Tab(4.25) ) )
         else:
            p.append(r'{\pard\sl317\tqr\tx%d \tqr\tx%d \tqr\tx%d ' % (Tab(1.75), Tab(2.35), Tab(3.08) ) )
         #
         
         newKey = '-'.join([str(level), str(grade), 'new'])
         retKey = '-'.join([str(level), str(grade), 'ret'])
         totKey = '-'.join([str(level), str(grade), 'tot'])
         
         if itbsLevelCounts[regionNum].has_key(newKey):
            newCt = itbsLevelCounts[regionNum][newKey]
         else:
            newCt = 0
         #
         newAccm += newCt
         
         if itbsLevelCounts[regionNum].has_key(retKey):
            retCt = itbsLevelCounts[regionNum][retKey]
         else:
            retCt = 0
         #
         retAccm += retCt
         
         if itbsLevelCounts[regionNum].has_key(totKey):
            totCt = itbsLevelCounts[regionNum][totKey]
         else:
            totCt = 0
         #
         totAccm += totCt
         
         # CHECK
         if newCt + retCt != totCt:
            errorCt += 1
            msg = 'ERROR -- new count + returning count != total count for ITBS region %d, grade %d' % (regionNum, grade)
            Log(msg)
         #
         
         if bNewRet:
            text = TEXT(r'\tab %d \tab %d \tab %d \tab %d \tab %d \par} ' % (level, grade, newCt, retCt, totCt), size=20 )
         else:
            text = TEXT(r'\tab %d \tab %d \tab %d \par} ' % (level, grade, totCt), size=20 )
         #
         print 'text = ', text.Data
         p.append( text )
      #
      section.append(p)
      
      p = Paragraph( ss.ParagraphStyles.Normal )
      
      if bNewRet:
         p.append( TEXT(r'{\pard\tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tab ITBS Total: \tab %d \tab %d \tab %d \par} ' %\
                        ( Tab(1.5), Tab(3.08), Tab(3.65), Tab(4.25), newAccm, retAccm, totAccm ), size=20, bold=True) )
      else:
         p.append( TEXT(r'{\pard\tx%d \tqr\tx%d \tab ITBS Total: \tab %d \par} ' %\
                        ( Tab(1.5), Tab(3.08), totAccm ), size=20, bold=True) )
      #
      section.append(p)
      
      # ITED
      p = Paragraph( ss.ParagraphStyles.Normal )
        
      p.append(r'______________________________________________________________\line ITED \line\line')
      if bNewRet:
         p.append(r'\tx%d \tx%d \tx%d \tx%d \tx%d ' % (Tab(1.5), Tab(2.1), Tab(2.8), Tab(3.25), Tab(4) ) )
         p.append( TEXT(r'\ulw\tab Level \tab Grade \tab New \tab Returning \tab Total', size=20, bold=False) )
      else:
         p.append(r'\tx%d \tx%d \tx%d ' % (Tab(1.5), Tab(2.1), Tab(2.8) ) )
         p.append( TEXT(r'\ulw\tab Level \tab Grade \tab Total', size=20, bold=False) )
      #      
      section.append(p)
      
      p = Paragraph( ss.ParagraphStyles.Normal )
      
      newAccm = retAccm = totAccm = 0
      
      for grade in range(9, 13):   # 9-12 inclusive
         level = grade + 6
         
         if bNewRet:
            p.append(r'{\pard\sl317\tqr\tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d ' % (Tab(1.75), Tab(2.35), Tab(3.08), Tab(3.65), Tab(4.25) ) )
         else:
            p.append(r'{\pard\sl317\tqr\tx%d \tqr\tx%d \tqr\tx%d ' % (Tab(1.75), Tab(2.35), Tab(3.08) ) )
         #
         
         newKey = '-'.join([str(level), str(grade), 'new'])
         retKey = '-'.join([str(level), str(grade), 'ret'])
         totKey = '-'.join([str(level), str(grade), 'tot'])
         
         if itedLevelCounts[regionNum].has_key(newKey):
            newCt = itedLevelCounts[regionNum][newKey]
         else:
            newCt = 0
         #
         newAccm += newCt
         
         if itedLevelCounts[regionNum].has_key(retKey):
            retCt = itedLevelCounts[regionNum][retKey]
         else:
            retCt = 0
         #
         retAccm += retCt
         
         if itedLevelCounts[regionNum].has_key(totKey):
            totCt = itedLevelCounts[regionNum][totKey]
         else:
            totCt = 0
         #
         totAccm += totCt
         
         # CHECK
         if newCt + retCt != totCt:
            errorCt += 1
            msg = 'ERROR -- new count + returning count != total count for ITED region %d, grade %d' % (regionNum, grade)
            Log(msg)
         #
         
         if bNewRet:
            text = TEXT(r'\tab %d \tab %d \tab %d \tab %d \tab %d \par} ' % (level, grade, newCt, retCt, totCt), size=20 )
         else:
            text = TEXT(r'\tab %d \tab %d \tab %d \par} ' % (level, grade, totCt), size=20 )
         #
         print 'text = ', text.Data
         p.append( text )
      #
      section.append(p)
      
      p = Paragraph( ss.ParagraphStyles.Normal )
      
      if bNewRet:
         p.append( TEXT(r'{\pard\tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tab ITED Total: \tab %d \tab %d \tab %d \par} ' %\
                        ( Tab(1.5), Tab(3.08), Tab(3.65), Tab(4.25), newAccm, retAccm, totAccm ), size=20, bold=True) )
      else:
         p.append( TEXT(r'{\pard\tx%d \tqr\tx%d \tab ITED Total: \tab %d \par} ' %\
                        ( Tab(1.5), Tab(3.08), totAccm ), size=20, bold=True) )
      #
      
      section.append(p)
      
      
      # Totals
      p = Paragraph( ss.ParagraphStyles.Normal )
        
      p.append(r'______________________________________________________________\line TOTALS \line\line')
      if bNewRet:
         p.append(r'\tx%d \tx%d \tx%d \tx%d ' % ( Tab(.2), Tab(2.8), Tab(3.25), Tab(4) ) )
         p.append( TEXT(r'\tab Students \ulw\tab New \tab Returning \tab Total', size=20, bold=False) )
      else:
         p.append(r'\tx%d \tx%d ' % ( Tab(.2), Tab(2.8) ) )
         p.append( TEXT(r'\tab Students \ulw\tab Total', size=20, bold=False) )
      #
      
      section.append(p)
      
      p = Paragraph( ss.ParagraphStyles.Normal )
      
      if bNewRet:
         p.append( TEXT(r'\par{\pard \tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tab ITBS: \tab %d \tab %d \tab %d \par} ' %\
                        ( Tab(.4), Tab(3.08), Tab(3.65), Tab(4.25), newItbsStudents[regionNum], retItbsStudents[regionNum], totItbsStudents[regionNum]),
                          size=20, bold=False ) )
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tab ITED: \tab %d \tab %d \tab %d \par} ' %\
                        ( Tab(.4), Tab(3.08), Tab(3.65), Tab(4.25), newItedStudents[regionNum], retItedStudents[regionNum], totItedStudents[regionNum]),
                          size=20, bold=False ) )
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tab ITBS + ITED: \tab %d \tab %d \tab %d \line\par} ' %\
                        ( Tab(.4), Tab(3.08), Tab(3.65), Tab(4.25), newItbsStudents[regionNum] + newItedStudents[regionNum],
                          retItbsStudents[regionNum] + retItedStudents[regionNum], totItbsStudents[regionNum] + totItedStudents[regionNum]),
                          size=20, bold=True ) )
         
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tab Level 14 \tab Grades 8 & 9: \tab %d \tab %d \tab %d \par} ' %\
                        ( Tab(.4), Tab(1.5), Tab(3.08), Tab(3.65), Tab(4.25), newLevel14Students[regionNum], retLevel14Students[regionNum], 
                          totLevel14Students[regionNum]), size=20, bold=False ) )
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tab Levels 14-9 & 15 \tab Grade 9: \tab %d \tab %d \tab %d \par} ' %\
                        ( Tab(.4), Tab(1.5), Tab(3.08), Tab(3.65), Tab(4.25), newGrade9Students[regionNum], retGrade9Students[regionNum], 
                          totGrade9Students[regionNum]), size=20, bold=False ) )
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tab Levels 17 & 18 \tab Grades 11 & 12: \tab %d \tab %d \tab %d \line\par} ' %\
                        ( Tab(.4), Tab(1.5), Tab(3.08), Tab(3.65), Tab(4.25), newGrades_11_12_students[regionNum], retGrades_11_12_students[regionNum], 
                          totGrades_11_12_students[regionNum]), size=20, bold=False ) )
         
         p.append(r'{\par\pard\tx%d \fs20\tab Families:\line\par} ' % ( Tab(.2) ) )
         
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITBS: (May include ITED students) \tab %d \par} ' %\
                        ( Tab(.4), Tab(4.25), itbsFamilies[regionNum] ), size=20, bold=False ) )
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITBS-Only: \tab %d \line\par} ' %\
                        ( Tab(.4), Tab(4.25), itbsOnlyFamilies[regionNum] ), size=20, bold=False ) )
         
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITED: (May include ITBS students) \tab %d \tab \par} ' %\
                        ( Tab(.4), Tab(4.25), itedFamilies[regionNum] ), size=20, bold=False ) )
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITED-Only: \tab %d \line\par} ' %\
                        ( Tab(.4), Tab(4.25), itedOnlyFamilies[regionNum] ), size=20, bold=False ) )
         
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab Total: \tab %d \par} ' %\
                        (  Tab(.4), Tab(4.25), totalFamilies[regionNum] ), size=20, bold=True ) )
         
      else:
         p.append( TEXT(r'\par{\pard \tx%d \tqr\tx%d \tab ITBS: \tab %d \par} ' %\
                        ( Tab(.4), Tab(3.08), totItbsStudents[regionNum]), size=20, bold=False ) )
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITED: \tab %d \par} ' %\
                        ( Tab(.4), Tab(3.08), totItedStudents[regionNum]), size=20, bold=False ) )
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITBS + ITED: \tab %d \line\par} ' %\
                        ( Tab(.4), Tab(3.08), totItbsStudents[regionNum] + totItedStudents[regionNum]),
                          size=20, bold=True ) )
         
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tqr\tx%d \tab Level 14 \tab Grades 8 & 9: \tab %d \par} ' %\
                        ( Tab(.4), Tab(1.5), Tab(3.08), totLevel14Students[regionNum]), size=20, bold=False ) )
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tqr\tx%d \tab Levels 14-9 & 15 \tab Grade 9: \tab %d \par} ' %\
                        ( Tab(.4), Tab(1.5), Tab(3.08), totGrade9Students[regionNum]), size=20, bold=False ) )
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tqr\tx%d \tab Levels 17 & 18 \tab Grades 11 & 12: \tab %d \line\par} ' %\
                        ( Tab(.4), Tab(1.5), Tab(3.08), totGrades_11_12_students[regionNum]), size=20, bold=False ) )
         
         p.append(r'{\par\pard\tx%d \fs20\tab Families:\line\par} ' % ( Tab(.2) ) )
         
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITBS: (May include ITED students) \tab %d \par} ' %\
                        ( Tab(.4), Tab(3.08), itbsFamilies[regionNum] ), size=20, bold=False ) )
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITBS-Only: \tab %d \line\par} ' %\
                        ( Tab(.4), Tab(3.08), itbsOnlyFamilies[regionNum] ), size=20, bold=False ) )
         
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITED: (May include ITBS students) \tab %d \tab \par} ' %\
                        ( Tab(.4), Tab(3.08), itedFamilies[regionNum] ), size=20, bold=False ) )
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITED-Only: \tab %d \line\par} ' %\
                        ( Tab(.4), Tab(3.08), itedOnlyFamilies[regionNum] ), size=20, bold=False ) )
         
         p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab Total: \tab %d \par} ' %\
                        (  Tab(.4), Tab(3.08), totalFamilies[regionNum] ), size=20, bold=True ) )
      #
      
      section.append(p)
      
      # Page Number
      p = Paragraph( ss.ParagraphStyles.Normal )
      p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
      section.append(p)
      
   # for regionNum
   
   
   #--------------------
   # Statewide totals
   #--------------------
   
   # Create a new section for statewide totals
   section = Section(paper=None, margins=regRptMargins, break_type=3, headery=None, footery=0, landscape=False) #, first_page_number=pageNum)
   doc.Sections.append( section )
   
   ss  = doc.StyleSheet
   p = Paragraph( ss.ParagraphStyles.Normal )
   
   # Page title
   p.append( TEXT( r'%d ICHE Statewide Test Count ' % (rptYear), size=24, bold=True) )
   
   p.append( TEXT( r'\tx%d \tx%d \tab %s \line' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
   
   section.append(p)
   
   #---------------------------
   # ITBS
   #---------------------------
   p = Paragraph( ss.ParagraphStyles.Normal )
     
   p.append(r'______________________________________________________________\line ITBS \line\line')
   if bNewRet:
      p.append(r'\tx%d \tx%d \tx%d \tx%d \tx%d ' % (Tab(1.5), Tab(2.1), Tab(2.8), Tab(3.25), Tab(4) ) )
      p.append( TEXT(r'\ulw\tab Level \tab Grade \tab New \tab Returning \tab Total', size=20, bold=False) )
   else:
      p.append(r'\tx%d \tx%d \tx%d ' % (Tab(1.5), Tab(2.1), Tab(2.8) ) )
      p.append( TEXT(r'\ulw\tab Level \tab Grade \tab Total', size=20, bold=False) )
   #
   section.append(p)
   
   p = Paragraph( ss.ParagraphStyles.Normal )
   
   newAccm = retAccm = totAccm = 0
   
   for grade in range(3, 10):   # 3-9 inclusive
      if grade == 9:
         level = 14
      else:
         level = grade + 6
      #
      
      if bNewRet:
         p.append(r'{\pard\sl317\tqr\tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d ' % (Tab(1.75), Tab(2.35), Tab(3.08), Tab(3.65), Tab(4.25) ) )
      else:
         p.append(r'{\pard\sl317\tqr\tx%d \tqr\tx%d \tqr\tx%d ' % (Tab(1.75), Tab(2.35), Tab(3.08) ) )
      #
      
      newKey = '-'.join([str(level), str(grade), 'new'])
      retKey = '-'.join([str(level), str(grade), 'ret'])
      totKey = '-'.join([str(level), str(grade), 'tot'])
      
      newCt = retCt = totCt = 0
      
      for regionNum in range(0, 19):   # 0-18 inclusive for indices (1-19 real-life)
         
         if itbsLevelCounts[regionNum].has_key(newKey):
            newCt += itbsLevelCounts[regionNum][newKey]
         #
         
         if itbsLevelCounts[regionNum].has_key(retKey):
            retCt += itbsLevelCounts[regionNum][retKey]
         #
         
         if itbsLevelCounts[regionNum].has_key(totKey):
            totCt += itbsLevelCounts[regionNum][totKey]
         #
         
      # End for Total all regions
      
      newAccm += newCt
      retAccm += retCt
      totAccm += totCt
      
      # CHECK
      if newCt + retCt != totCt:
         errorCt += 1
         msg = 'ERROR -- new count + returning count != total count for ITBS region %d, grade %d' % (regionNum, grade)
         Log(msg)
      #
      
      if bNewRet:
         text = TEXT(r'\tab %d \tab %d \tab %d \tab %d \tab %d \par} ' % (level, grade, newCt, retCt, totCt), size=20 )
      else:
         text = TEXT(r'\tab %d \tab %d \tab %d \par} ' % (level, grade, totCt), size=20 )
      #
      
      print 'text = ', text.Data
      p.append( text )
      
   #   For each grade
   
   section.append(p)
   
   p = Paragraph( ss.ParagraphStyles.Normal )
   
   if bNewRet:
      p.append( TEXT(r'{\pard\tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tab ITBS Total: \tab %d \tab %d \tab %d \par} ' %\
                     ( Tab(1.5), Tab(3.08), Tab(3.65), Tab(4.25), newAccm, retAccm, totAccm ), size=20, bold=True) )
   else:
      p.append( TEXT(r'{\pard\tx%d \tqr\tx%d \tab ITBS Total: \tab %d \par} ' %\
                     ( Tab(1.5), Tab(3.08), totAccm ), size=20, bold=True) )
   #
   
   section.append(p)
   
   # ITED
   p = Paragraph( ss.ParagraphStyles.Normal )
     
   p.append(r'______________________________________________________________\line ITED \line\line')
   if bNewRet:
      p.append(r'\tx%d \tx%d \tx%d \tx%d \tx%d ' % (Tab(1.5), Tab(2.1), Tab(2.8), Tab(3.25), Tab(4) ) )
      p.append( TEXT(r'\ulw\tab Level \tab Grade \tab New \tab Returning \tab Total', size=20, bold=False) )
   else:
      p.append(r'\tx%d \tx%d \tx%d ' % (Tab(1.5), Tab(2.1), Tab(2.8) ) )
      p.append( TEXT(r'\ulw\tab Level \tab Grade \tab Total', size=20, bold=False) )
   #
   section.append(p)
   
   p = Paragraph( ss.ParagraphStyles.Normal )
   
   newAccm = retAccm = totAccm = 0
   
   for grade in range(9, 13):   # 9-12 inclusive
      level = grade + 6
      
      if bNewRet:
         p.append(r'{\pard\sl317\tqr\tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d ' % (Tab(1.75), Tab(2.35), Tab(3.08), Tab(3.65), Tab(4.25) ) )
      else:
         p.append(r'{\pard\sl317\tqr\tx%d \tqr\tx%d \tqr\tx%d ' % (Tab(1.75), Tab(2.35), Tab(3.08) ) )
      #
      
      newKey = '-'.join([str(level), str(grade), 'new'])
      retKey = '-'.join([str(level), str(grade), 'ret'])
      totKey = '-'.join([str(level), str(grade), 'tot'])
      
      newCt = retCt = totCt = 0
      
      for regionNum in range(0, 19):   # 0-18 inclusive for indices (1-19 real-life)
         
         if itedLevelCounts[regionNum].has_key(newKey):
            newCt += itedLevelCounts[regionNum][newKey]
         #
         
         if itedLevelCounts[regionNum].has_key(retKey):
            retCt += itedLevelCounts[regionNum][retKey]
         #
         
         if itedLevelCounts[regionNum].has_key(totKey):
            totCt += itedLevelCounts[regionNum][totKey]
         #
         
      # End for Total all regions
      
      newAccm += newCt
      retAccm += retCt
      totAccm += totCt
      
      # CHECK
      if newCt + retCt != totCt:
         errorCt += 1
         msg = 'ERROR -- new count + returning count != total count for ITED region %d, grade %d' % (regionNum, grade)
         Log(msg)
      #
      
      if bNewRet:
         text = TEXT(r'\tab %d \tab %d \tab %d \tab %d \tab %d \par} ' % (level, grade, newCt, retCt, totCt), size=20 )
      else:
         text = TEXT(r'\tab %d \tab %d \tab %d \par} ' % (level, grade, totCt), size=20 )
      #
      
      print 'text = ', text.Data
      p.append( text )
      
   # For each grade
   
   section.append(p)
   
   p = Paragraph( ss.ParagraphStyles.Normal )
   
   if bNewRet:
      p.append( TEXT(r'{\pard\tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tab ITED Total: \tab %d \tab %d \tab %d \par} ' %\
                     ( Tab(1.5), Tab(3.08), Tab(3.65), Tab(4.25), newAccm, retAccm, totAccm ), size=20, bold=True) )
   else:
      p.append( TEXT(r'{\pard\tqr\tx%d \tqr\tx%d \tab ITED Total: \tab %d \par} ' %\
                     ( Tab(1.5), Tab(3.08), totAccm ), size=20, bold=True) )
   #
   
   section.append(p)
   
   
   # Totals
   p = Paragraph( ss.ParagraphStyles.Normal )
   
   p.append(r'______________________________________________________________\line TOTALS \line\line')
   if bNewRet:
      p.append(r'\tx%d \tx%d \tx%d \tx%d ' % ( Tab(.2), Tab(2.8), Tab(3.25), Tab(4) ) )
      p.append( TEXT(r'\tab Students \ulw\tab New \tab Returning \tab Total', size=20, bold=False) )
   else:
      p.append(r'\tx%d \tx%d ' % ( Tab(.2), Tab(2.8) ) )
      p.append( TEXT(r'\tab Students \ulw\tab Total', size=20, bold=False) )
   #
   
   section.append(p)
   
   p = Paragraph( ss.ParagraphStyles.Normal )
   
   stateNewItbsStudents    = 0
   stateRetItbsStudents    = 0
   stateNewItedStudents    = 0
   stateRetItedStudents    = 0
   stateNewLevel14Students = 0
   stateRetLevel14Students = 0
   stateNewGrade9Students  = 0
   stateRetGrade9Students  = 0
   stateNewGrades_11_12_students = 0
   stateRetGrades_11_12_students = 0
   
   stateItbsFamilies      = 0
   stateItedFamilies      = 0
   stateTotalFamilies     = 0
   stateItbsOnlyFamilies  = 0
   stateItedOnlyFamilies  = 0
   
   for regionNum in range(0, 19):   # 0-18 inclusive for indices (1-19 real-life)
      stateNewItbsStudents    += newItbsStudents[regionNum]
      stateRetItbsStudents    += retItbsStudents[regionNum]
      stateNewItedStudents    += newItedStudents[regionNum]
      stateRetItedStudents    += retItedStudents[regionNum]
      stateNewLevel14Students += newLevel14Students[regionNum]
      stateRetLevel14Students += retLevel14Students[regionNum]
      stateNewGrade9Students  += newGrade9Students[regionNum]
      stateRetGrade9Students  += retGrade9Students[regionNum]
      stateNewGrades_11_12_students += newGrades_11_12_students[regionNum]
      stateRetGrades_11_12_students += retGrades_11_12_students[regionNum]
      stateItbsFamilies       += itbsFamilies[regionNum]
      stateItedFamilies       += itedFamilies[regionNum]
      stateItbsOnlyFamilies   += itbsOnlyFamilies[regionNum]
      stateItedOnlyFamilies   += itedOnlyFamilies[regionNum]
      stateTotalFamilies      += totalFamilies[regionNum]
   #
   
   if bNewRet:
      p.append( TEXT(r'\par{\pard \tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tab ITBS: \tab %d \tab %d \tab %d \par} ' %\
                     ( Tab(.4), Tab(3.08), Tab(3.65), Tab(4.25), stateNewItbsStudents, stateRetItbsStudents,
                       stateNewItbsStudents + stateRetItbsStudents), size=20, bold=False ) )
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tab ITED: \tab %d \tab %d \tab %d \par} ' %\
                     ( Tab(.4), Tab(3.08), Tab(3.65), Tab(4.25), stateNewItedStudents, stateRetItedStudents,
                       stateNewItedStudents + stateRetItedStudents), size=20, bold=False ) )
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tab ITBS + ITED: \tab %d \tab %d \tab %d \line\par} ' %\
                     ( Tab(.4), Tab(3.08), Tab(3.65), Tab(4.25), stateNewItbsStudents + stateNewItedStudents,
                       stateRetItbsStudents + stateRetItedStudents,
                       stateNewItbsStudents + stateNewItedStudents + stateRetItbsStudents + stateRetItedStudents),
                       size=20, bold=True ) )
      
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tab Level 14 \tab Grades 8 & 9: \tab %d \tab %d \tab %d \par} ' %\
                     ( Tab(.4), Tab(1.5), Tab(3.08), Tab(3.65), Tab(4.25), stateNewLevel14Students, stateRetLevel14Students, 
                        stateNewLevel14Students + stateRetLevel14Students), size=20, bold=False ) )
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tab Levels 14-9 & 15 \tab Grade 9: \tab %d \tab %d \tab %d \par} ' %\
                     ( Tab(.4), Tab(1.5), Tab(3.08), Tab(3.65), Tab(4.25), stateNewGrade9Students, stateRetGrade9Students, 
                        stateNewGrade9Students + stateRetGrade9Students), size=20, bold=False ) )
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tqr\tx%d \tab Levels 17 & 18 \tab Grades 11 & 12: \tab %d \tab %d \tab %d \line\par} ' %\
                     ( Tab(.4), Tab(1.5), Tab(3.08), Tab(3.65), Tab(4.25), stateNewGrades_11_12_students, stateRetGrades_11_12_students, 
                       stateNewGrades_11_12_students + stateRetGrades_11_12_students), size=20, bold=False ) )
      
      p.append(r'{\par\pard\tx%d \fs20\tab Families:\line\par} ' % ( Tab(.2) ) )
      
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITBS:  (May include ITED students)\tab %d \par} ' %\
                     ( Tab(.4), Tab(4.25), stateItbsFamilies ), size=20, bold=False ) )
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITBS-Only: \tab %d \line\par} ' %\
                     ( Tab(.4), Tab(4.25), stateItbsOnlyFamilies ), size=20, bold=False ) )
      
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITED:  (May include ITBS students)\tab %d \par} ' %\
                     ( Tab(.4), Tab(4.25), stateItedFamilies ), size=20, bold=False ) )
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITED-Only: \tab %d \line\par} ' %\
                     ( Tab(.4), Tab(4.25), stateItedOnlyFamilies ), size=20, bold=False ) )
      
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab Total: \tab %d \par} ' %\
                     (  Tab(.4), Tab(4.25), stateTotalFamilies), size=20, bold=True ) )
   else:
      p.append( TEXT(r'\par{\pard \tx%d \tqr\tx%d \tab ITBS: \tab %d \par} ' %\
                     ( Tab(.4), Tab(3.08), 
                       stateNewItbsStudents + stateRetItbsStudents), size=20, bold=False ) )
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITED: \tab %d \par} ' %\
                     ( Tab(.4), Tab(3.08), 
                       stateNewItedStudents + stateRetItedStudents), size=20, bold=False ) )
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITBS + ITED: \tab %d \line\par} ' %\
                     ( Tab(.4), Tab(3.08), 
                       stateNewItbsStudents + stateNewItedStudents + stateRetItbsStudents + stateRetItedStudents),
                       size=20, bold=True ) )
      
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tqr\tx%d \tab Level 14 \tab Grades 8 & 9: \tab %d \par} ' %\
                     ( Tab(.4), Tab(1.5), Tab(3.08), 
                        stateNewLevel14Students + stateRetLevel14Students), size=20, bold=False ) )
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tqr\tx%d \tab Levels 14-9 & 15 \tab Grade 9: \tab %d \par} ' %\
                     ( Tab(.4), Tab(1.5), Tab(3.08), 
                        stateNewGrade9Students + stateRetGrade9Students), size=20, bold=False ) )
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tqr\tx%d \tab Levels 17 & 18 \tab Grades 11 & 12: \tab %d \line\par} ' %\
                     ( Tab(.4), Tab(1.5), Tab(3.08),
                       stateNewGrades_11_12_students + stateRetGrades_11_12_students), size=20, bold=False ) )
            
      p.append(r'{\par\pard\tx%d \fs20\tab Families:\line\par} ' % ( Tab(.2) ) )
      
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITBS:  (May include ITED students)\tab %d \par} ' %\
                     ( Tab(.4), Tab(3.08), stateItbsFamilies ), size=20, bold=False ) )
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITBS-Only: \tab %d \line\par} ' %\
                     ( Tab(.4), Tab(3.08), stateItbsOnlyFamilies ), size=20, bold=False ) )
      
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITED:  (May include ITBS students)\tab %d \par} ' %\
                     ( Tab(.4), Tab(3.08), stateItedFamilies ), size=20, bold=False ) )
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab ITED-Only: \tab %d \line\par} ' %\
                     ( Tab(.4), Tab(3.08), stateItedOnlyFamilies ), size=20, bold=False ) )
      
      p.append( TEXT(r'{\pard \tx%d \tqr\tx%d \tab Total: \tab %d \par} ' %\
                     ( Tab(.4), Tab(3.08), stateTotalFamilies), size=20, bold=True ) )
   #
   
   section.append(p)
   
   p = Paragraph( ss.ParagraphStyles.Normal )
   p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
   section.append(p)
   
   # Get Date-time stamp
   #t = time.localtime()
   #date_time_stamp = str(t[0]) + '-%02d' % t[1] + '-%02d' % t[2] + '_%02d' % t[3] + '-%02d' % t[4]
   
   if bNewRet:
      filename = './output/TestCountReport_' + date_time_stamp + '_WithNewRet.rtf'
   else:
      filename = './output/TestCountReport_' + date_time_stamp + '.rtf'
   #
   
   # Render and print the RTF
   DR = Renderer()                                           # From PyRTF
   DR.Write( doc, file( filename, 'w' ) )
   
   
   #----------------------------------------------------------------------------
   # Final error count
   #
   print 'TestCountReports Error count =', errorCt
   
# End TestCountReports()


def AnswerSheetsByRegionLevelReport(cursor, rptYear, testingRegions):
   errorCt = 0
   
   # Write the report
   doc = Document()
   
   # Margins are top, left, bottom, right
   regRptMargins = MarginsPropertySet(top=1000, left=720, bottom=720, right=720)
   
   maxPageLines = 31
   numPageNumberLines    = 2
   numRegionHeaderLines  = 2
   numLevelHeaderLines   = 3
   numLevelFooterLines   = 3
   minNumStudentsOnPageA = 2   # Min number of students in a level on the first of the pages for a single level
   minNumStudentsOnPageB = 2   # Min number of students in a level on the last of the pages for a single level
   bAddedPageBreak = False
   
   for region in testingRegions:
      
      linesLeftOnThisPage = maxPageLines
      
      # Create a new section for each region
      section = Section(paper=Paper('Landscape', '100', 'Landscape 8.5 x 11', 15480, 12240),
                        margins=regRptMargins, break_type=3, headery=None, footery=0, landscape=True) #, first_page_number=pageNum)
      #section.Footer.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20 Page \chpgn')  # This works    # Centering;  looks like centers anyway: \qc
      doc.Sections.append( section )
      
      ss  = doc.StyleSheet
      
      # Page title
      p = Paragraph( ss.ParagraphStyles.Normal )
      p.append( TEXT( r'%d ICHE Tested Students Answer Sheets by Region / Level ' % (rptYear), size=24, bold=True) )
      p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
      p.append( TEXT( r'\tab   %d %s \line ' % (region.regionNum, regionNames[region.regionNum-1]), size=24, bold=True) )
      section.append(p)
      
      #print 'region', region.regionNum   # ### DEBUG
      
      linesLeftOnThisPage -= numRegionHeaderLines
      
      # Levels
      for level in range(9, 19):  # Levels 9-18 inclusive
         levelCt = 0
         
         #print 'level', level # DEBUG ###
         
         # Look ahead to find the number of students for level
         numTotalStudentsThisLevel = 0
         for family in region.families:
            for testingStudent in family.testingStudents:
               a_testHist = testingStudent.testing_history
               
               if a_testHist.level == level:
                  numTotalStudentsThisLevel += 1
               #
            # End for testing student
         # End for family
         
         
         bAddedPageBreak = False
         
         #------------------------------
         # Add page break between levels
         #------------------------------
         #numLevelFooterLines   = 3 \___ using the larger -- could be empty level
         #minNumStudentsOnPageA = 2 /         
         if    (linesLeftOnThisPage < (numLevelHeaderLines + numLevelFooterLines + numPageNumberLines) ) \
            or (    (linesLeftOnThisPage < numLevelHeaderLines + numTotalStudentsThisLevel + numLevelFooterLines + numPageNumberLines) \
                and (numTotalStudentsThisLevel < 4) \
               ):
            p = Paragraph( ss.ParagraphStyles.Normal )
            p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
            section.append(p)
            
            section.append(r'\page')
            #bAddedPageBreak = True
            linesLeftOnThisPage = maxPageLines
            
            # Page title
            p = Paragraph( ss.ParagraphStyles.Normal )
            p.append( TEXT( r'%d ICHE Tested Students Answer Sheets by Region / Level ' % (rptYear), size=24, bold=True) )
            p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
            p.append( TEXT( r'\tab   %d %s \line ' % (region.regionNum, regionNames[region.regionNum-1]), size=24, bold=True) )
            section.append(p)
            
            linesLeftOnThisPage -= numRegionHeaderLines
         #
         
         # Print the level header even if there are no students in this region and level
         #numLevelFooterLines   = 3 \___ using the larger -- could be empty level
         #minNumStudentsOnPageA = 2 /
         if  linesLeftOnThisPage >= (numLevelHeaderLines + numLevelFooterLines + numPageNumberLines):
            section.append(r'_________________________________________________________________________________________________________________')
            section.append( r'\fs20\tx%d\tx%d\tx%d\b Level %d\b0\tab Peters\tab Springdale Schools\tab Form/Grade/State\line ' %\
                            ( Tab(4), Tab(5.5), Tab(8.5), level ) )
            linesLeftOnThisPage -= numLevelHeaderLines
         #
         
         p = Paragraph( ss.ParagraphStyles.Normal )
         studentCt = 0
         
         for family in region.families:
            for testingStudent in family.testingStudents:
               a_student = testingStudent.student
               a_testHist = testingStudent.testing_history
               
               if a_testHist.level == level:
                  studentCt += 1
                 
                  regionStr = 'R-' + str(region.regionNum) + '   ' + regionNames[region.regionNum - 1]
                  campusStr = 'Campus  ' + a_testHist.campus
                  formType = 'A'
                  stateAbbrv = 'ID'
                  
                  month = str(a_student.dob)
                  year = str(a_student.dob)
                  if month == 'None':
                     dob = 'None'
                     print 'Error -- dob is "None" for student_id ' + str(a_student.student_id)
                     errorCt += 1
                  else:
                     monthNumStr= month[5:7]
                     monthNum = int(monthNumStr) - 1
                     monthAbbrv = monthAbbrNames[monthNum]
                     yearAbbrv = year[2:4]
                     
                     dob = monthAbbrv + '  ' + yearAbbrv
                  #
                  p.append( TEXT( r'{\pard\sl300\tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tab %s \tab %s \tab %s \tab %s \tab %s \tab %s \tab %s \tab %s \tab %s \par} ' %\
                                  (Tab(.25), Tab(2), Tab(3.5), Tab(4), Tab(5.5), Tab(7.5), Tab(8.6), Tab(9), Tab(9.4),
                                   a_student.l_name, a_student.f_name, a_student.gender.upper(), dob, regionStr, 
                                   campusStr, formType, a_testHist.grade, stateAbbrv), size=20, bold=False) )
                  
                  print a_student.l_name + ', ' + a_student.f_name   # ### DEBUG                  
                  #if a_student.f_name == 'Ashley' and a_student.l_name == 'Lucas':
                  #   dummy = 'brkpt'
                  ##
                  
                  levelCt += 1               # levelCt = Number of students at level currently being processed
                  linesLeftOnThisPage -= 1
                  
                  bAddedPageBreak = False    # Don't add a page break if its to be added below due to having
                                             # reached the end of the students in this region because the 
                                             # section break for the region will add a page break
                  
                  #-------------------------  
                  # Add page break mid-level
                  #-------------------------
                  if linesLeftOnThisPage < numLevelFooterLines + numPageNumberLines:
                     section.append(p)
                     
                     p = Paragraph( ss.ParagraphStyles.Normal )
                     p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
                     section.append(p)
                     
                     section.append(r'\page')
                     bAddedPageBreak = True
                     linesLeftOnThisPage = maxPageLines
                     
                     # Page title
                     p = Paragraph( ss.ParagraphStyles.Normal )
                     p.append( TEXT( r'%d ICHE Tested Students Answer Sheets by Region / Level ' % (rptYear), size=24, bold=True) )
                     p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
                     p.append( TEXT( r'\tab   %d %s \line ' % (region.regionNum, regionNames[region.regionNum-1]), size=24, bold=True) )
                     section.append(p)
                     
                     linesLeftOnThisPage -= numRegionHeaderLines
                     
                     section.append(r'_________________________________________________________________________________________________________________')
                     p = Paragraph( ss.ParagraphStyles.Normal )
                     section.append( r'\fs20\tx%d\tx%d\tx%d\b Level %d\b0\tab Peters\tab Springdale Schools\tab Form/Grade/State\line ' %\
                                     ( Tab(4), Tab(5.5), Tab(8.5), level ) )
                     section.append(p)
                     
                     linesLeftOnThisPage -= numLevelHeaderLines
                     
                     p = Paragraph( ss.ParagraphStyles.Normal )
                  #
                  
               # If student level matches the current level being processed
            # End for testing student
         # End for family
         
         # Not a new page, but we have writen students for the current level
         section.append(p)
         
         # Print total count for the level
         p = Paragraph( ss.ParagraphStyles.Normal )
         p.append( TEXT( r'{\pard\tx%d \tab Level  %d  Count  %d\par} ' % (Tab(8.4), level, levelCt), size=20, bold=True) )
         section.append(p)
         linesLeftOnThisPage -= numLevelFooterLines
         
         if region.regionNum == 14 and level == 18:
            brkpt = True
         #
         
      # End for level
      
      # Finished region so add a newline
      if not bAddedPageBreak:
         p = Paragraph( ss.ParagraphStyles.Normal )
         p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
         section.append(p)
         
         #p = Paragraph( ss.ParagraphStyles.Normal )
      #
      
   # End for region
   
   ## Page number on last page
   #p = Paragraph( ss.ParagraphStyles.Normal )
   #p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
   #section.append(p)
   
   filename = './output/AnswerSheetsByRegionLevel_' + date_time_stamp + '.rtf'
   
   # Render and print the RTF
   DR = Renderer()                             # From PyRTF
   DR.Write( doc, file( filename, 'w' ) )
   
   #----------------------------------------------------------------------------
   # Final error count
   #
   print 'AnswerSheetsByRegionLevelReport Error count =', errorCt
   
#  AnswerSheetsByRegionLevelReport()


def AnswerSheetsByLevelRegionReport(cursor, rptYear, testingRegions):
   errorCt = 0
   
   # Write the report
   doc = Document()
   
   # Margins are top, left, bottom, right
   regRptMargins = MarginsPropertySet(top=1000, left=720, bottom=720, right=720)
   
   maxPageLines = 31
   numPageNumberLines    = 2
   numLevelHeaderLines   = 3
   numRegionHeaderLines  = 3
   numRegionFooterLines  = 3
   minNumStudentsOnPageA = 2   # Min number of students in a level on the first of the pages for a single level
   minNumStudentsOnPageB = 2   # Min number of students in a level on the last of the pages for a single level
   bAddedPageBreak = False
   
   # Levels
   for level in range(9, 19):   # 9-18 inclusive
      linesLeftOnThisPage = maxPageLines
      
      # Create a new section for each level
      section = Section(paper=Paper('Landscape', '100', 'Landscape 8.5 x 11', 15480, 12240),
                        margins=regRptMargins, break_type=3, headery=None, footery=0, landscape=True) #, first_page_number=pageNum)
      doc.Sections.append( section )
      ss  = doc.StyleSheet
      
      # Page title
      if level == 14:
         grade = "8 / 9"
      else:
         grade = str(level - 6)
      #
      
      # Page title
      p = Paragraph( ss.ParagraphStyles.Normal )
      p.append( TEXT( r'%d ICHE Tested Students Answer Sheets by Level / Region        ' % ( rptYear ), size=24, bold=True) )
      p.append( TEXT( r' \b0 %s        ' % (date_stamp), size=16, bold=False) )
      p.append( TEXT( r' Level  %d    Grade  %s \line ' % (level, grade), size=24, bold=True) )
      section.append(p)
      
      linesLeftOnThisPage -= numLevelHeaderLines
      
      # Regions
      for regionNum in range(1, 20):   # 1-19 inclusive
         regionCt = 0
         
         print 'region', regionNum   # DEBUG ###
         
         # Look ahead to number of students for this region
         numTotalStudentsThisRegion = 0
         for region in testingRegions:
            if region.regionNum == regionNum:
               
               for family in region.families:
                  for testingStudent in family.testingStudents:
                     a_testHist = testingStudent.testing_history
                     
                     if a_testHist.level == level:
                        numTotalStudentsThisRegion += 1
                     #
                  # End for testing student
               # End for family
            #
         # End for region
         
         
         bAddedPageBreak = False
         
         #-------------------------------
         # Add page break between regions
         #-------------------------------
         # numRegionFooterLines  = 3 \__ using the larger -- could be empty region
         # minNumStudentsOnPageA = 2 /         
         if    (linesLeftOnThisPage < (numRegionHeaderLines + numRegionFooterLines + numPageNumberLines) ) \
            or (    (linesLeftOnThisPage < numRegionHeaderLines + numTotalStudentsThisRegion + numRegionFooterLines + numPageNumberLines) \
                and (numTotalStudentsThisRegion < 4) \
               ):
            p = Paragraph( ss.ParagraphStyles.Normal )
            p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
            section.append(p)
            
            section.append(r'\page')
            #bAddedPageBreak = True
            linesLeftOnThisPage = maxPageLines
            
            # Page title
            p = Paragraph( ss.ParagraphStyles.Normal )
            p.append( TEXT( r'%d ICHE Tested Students Answer Sheets by Level / Region        ' % ( rptYear ), size=24, bold=True) )
            p.append( TEXT( r' \b0 %s        ' % (date_stamp), size=16, bold=False) )
            p.append( TEXT( r' Level  %d    Grade  %s \line ' % (level, grade), size=24, bold=True) )
            section.append(p) 
            
            linesLeftOnThisPage -= numLevelHeaderLines            
         #
         
         # Print the region header even if there are no students in this level and region
         # numRegionFooterLines  = 3 \__ using the larger -- could be empty region
         # minNumStudentsOnPageA = 2 /
         if  linesLeftOnThisPage >= (numRegionHeaderLines + numRegionFooterLines + numPageNumberLines):
            section.append(r'_________________________________________________________________________________________________________________')
            p = Paragraph( ss.ParagraphStyles.Normal )
            p.append( r'\fs20\tx%d\tx%d\tx%d\b Region %d\b0\tab Peters\tab Springdale Schools\tab Form/Grade/State\line ' %\
                      ( Tab(4), Tab(5.5), Tab(8.5), regionNum ) )
            section.append(p)
            linesLeftOnThisPage -= numRegionHeaderLines
         #
         
         for region in testingRegions:
            if region.regionNum == regionNum:
               
               p = Paragraph( ss.ParagraphStyles.Normal )
               studentCt = 0
               
               for family in region.families:
                  for testingStudent in family.testingStudents:
                     a_student = testingStudent.student
                     a_testHist = testingStudent.testing_history
                     
                     if a_testHist.level == level:
                        studentCt += 1
                        
                        regionStr = 'R-' + str(region.regionNum) + '   ' + regionNames[region.regionNum - 1]
                        campusStr = 'Campus  ' + a_testHist.campus
                        formType = 'A'
                        stateAbbrv = 'ID'
                        
                        month = str(a_student.dob)
                        year = str(a_student.dob)
                        if month == 'None':
                           dob = 'None'
                           print 'Error -- dob is "None" for student_id ' + str(a_student.student_id)
                           errorCt += 1
                        else:
                           monthNumStr= month[5:7]
                           monthNum = int(monthNumStr) - 1
                           monthAbbrv = monthAbbrNames[monthNum]
                           yearAbbrv = year[2:4]
                           
                           dob = monthAbbrv + '  ' + yearAbbrv
                        #
                        
                        p.append( TEXT( r'{\pard\sl300\tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tx%d \tab %s \tab %s \tab %s \tab %s \tab %s \tab %s \tab %s \tab %s \tab %s \par} ' %\
                                        (Tab(.25), Tab(2), Tab(3.5), Tab(4), Tab(5.5), Tab(7.5), Tab(8.6), Tab(9), Tab(9.4),
                                         a_student.l_name, a_student.f_name, a_student.gender.upper(), dob, regionStr, 
                                         campusStr, formType, a_testHist.grade, stateAbbrv), size=20, bold=False) )
                        
                        print a_student.l_name + ', ' + a_student.f_name   # ### DEBUG 
                        #if a_student.l_name == 'McCulloch':   # DEBUG
                        #   breakpt  = True
                        ##
                        
                        regionCt += 1
                        linesLeftOnThisPage -= 1
                        
                        bAddedPageBreak = False    # Don't add a page break if its to be added below due to having
                                                   # reached the end of the students in this region because the 
                                                   # section break for the region will add a page break
                        
                        #-------------------------- 
                        # Add page break mid-region
                        #--------------------------                                                  
                        #if     (linesLeftOnThisPage < minNumStudentsOnPageB + numRegionFooterLines + 1) \
                        #   and (numTotalStudentsThisRegion >= studentCt + minNumStudentsOnPageB):
                        #   section.append(p)
                        if  linesLeftOnThisPage < numRegionFooterLines + numPageNumberLines:
                           section.append(p)
                           
                           p = Paragraph( ss.ParagraphStyles.Normal )
                           p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
                           section.append(p)
                           
                           section.append(r'\page')
                           bAddedPageBreak = True
                           linesLeftOnThisPage = maxPageLines
                           
                           # Page title
                           p = Paragraph( ss.ParagraphStyles.Normal )
                           p.append( TEXT( r'%d ICHE Tested Students Answer Sheets by Level / Region        ' % ( rptYear ), size=24, bold=True) )
                           p.append( TEXT( r' \b0 %s        ' % (date_stamp), size=16, bold=False) )
                           p.append( TEXT( r' Level  %d    Grade  %s \line ' % (level, grade), size=24, bold=True) )
                           section.append(p)                           
                           
                           linesLeftOnThisPage -= numLevelHeaderLines
                           
                           section.append(r'_________________________________________________________________________________________________________________')
                           p = Paragraph( ss.ParagraphStyles.Normal )
                           p.append( r'\fs20\tx%d\tx%d\tx%d\b Region %d\b0\tab Peters\tab Springdale Schools\tab Form/Grade/State\line ' %\
                                     ( Tab(4), Tab(5.5), Tab(8.5), regionNum ) )
                           section.append(p)
                           
                           linesLeftOnThisPage -= numRegionHeaderLines                           
                           
                           p = Paragraph( ss.ParagraphStyles.Normal )
                        #
                        
                     # If student level matches the current level being processed
                  # End for testing student
               # End for family
               section.append(p)
               
               p = Paragraph( ss.ParagraphStyles.Normal )
               p.append( TEXT( r'\pard\tx%d \tab Region  %d  Count  %d \par' % (Tab(8.3), regionNum, regionCt), size=20, bold=True) )
               section.append(p)
               linesLeftOnThisPage -= numRegionFooterLines
               
            # If region num matches
         # for region
      # for region num in sequence 1-19
      
      # Finished level so add a newline
      if not bAddedPageBreak:
         p = Paragraph( ss.ParagraphStyles.Normal )
         p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
         section.append(p)
         
         #section.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
         #p = Paragraph( ss.ParagraphStyles.Normal )
      #
      
   # End for level
   
   filename = './output/AnswerSheetsByLevelRegion_' + date_time_stamp + '.rtf'
   
   # Render and print the RTF
   DR = Renderer()                                           # From PyRTF
   DR.Write( doc, file( filename, 'w' ) )
   
   
   #----------------------------------------------------------------------------
   # Final error count
   #
   print 'AnswerSheetsByLevelRegionReport Error count =', errorCt
   
#  AnswerSheetsByLevelRegionReport()


def CurrentMemberReports(sortedMembersByRegion):
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
   
   for regionNum in range(1, 20):
      linesLeftOnThisPage = maxPageLines
      
      regionDoc = Document()
      
      # Create a new section for each region
      section = Section(paper=None, margins=regRptMargins, break_type=3, headery=None, footery=0, landscape=False) #, first_page_number=pageNum)
      combinedDoc.Sections.append( section )
      regionDoc.Sections.append( section )
      
      p = Paragraph( ss.ParagraphStyles.Normal )
      p.append( TEXT( r'ICHE Current Members by Region ', size=24, bold=True) )
      p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
      p.append( TEXT( r'\tab   %d %s \line ' % (regionNum, regionNames[regionNum - 1]), size=24, bold=True) )
      section.append(p)
      
      p = Paragraph( ss.ParagraphStyles.Normal )
      p.append( r'\pard\tx%d \tx%d \tx%d \tx%d \ulw\b\fs20 Name \tab Address \tab Phone/Email \tab Region \tab Expires\line ' %\
                ( Tab(2.0), Tab(4.4), Tab(5.9), Tab(6.5) ) )
      section.append(p)
      
      linesLeftOnThisPage -= numRegionHeaderLines
      
      curMemberCt = len(sortedMembersByRegion[regionNum])
      curMemberNum =0
      for currentMember in sortedMembersByRegion[regionNum]:
         #track the member number (count)
         curMemberNum += 1
         #name is first on the header
         name = currentMember.mother_l_name + ', ' + currentMember.mother_f_name
         #phone number
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
         
         # Change street to CapWords
         #streetParts = currentMember.street
         #for part in streetParts:
            #if part != 'PO':
               #part.capitalize()
         ##
         #street = ''.join(streetParts)
         #street = string.capwords(currentMember.street)
         street = currentMember.street.strip()
         
         p = Paragraph( ss.ParagraphStyles.Normal )
         p.append( r'\fs20\tx%d \tx%d \tx%d \tx%d %s \tab %s \tab %s \tab %d \tab %s \line\tab %s, %s %s \tab %s \line ' %\
                         (Tab(2.0), Tab(4.4), Tab(5.9), Tab(6.5),
                          name, street, phone, currentMember.region, 
                         currentMember.membership_expires, currentMember.city.strip(), 
                         currentMember.state, currentMember.zip, currentMember.email.strip() ) )
         section.append(p)
         
         linesLeftOnThisPage -= numMemberLines
         
         bAddedPageBreak = False
         
         if linesLeftOnThisPage < 4:
            if curMemberNum < curMemberCt:
               p = Paragraph( ss.ParagraphStyles.Normal )
               #removed the following line 3.8.2013
               #p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
               p.append( r'{\insrsid2691151 Page }{\field{\*\fldinst {\insrsid2691151  PAGE }}{\fldrslt {\insrsid2691151 1}}}{\insrsid2691151  of }{\field{\*\fldinst {\insrsid2691151  NUMPAGES }}{\fldrslt {\insrsid11226526 2}}}{\insrsid2691151 \par }}')
               section.append(p)
               section.append(r'\page')
               
               linesLeftOnThisPage = maxPageLines
               bAddedPageBreak = True
            #
            
            if curMemberNum < curMemberCt:
               p = Paragraph( ss.ParagraphStyles.Normal )
               p.append( TEXT( r'ICHE Current Members by Region ', size=24, bold=True) )
               p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
               p.append( TEXT( r'\tab   %d %s \line ' % (regionNum, regionNames[regionNum - 1]), size=24, bold=True) )
               section.append(p) 
               
               p = Paragraph( ss.ParagraphStyles.Normal )
               p.append( r'\pard\tx%d \tx%d \tx%d \tx%d \ulw\b\fs20 Name \tab Address \tab Phone/Email \tab Region \tab Expires\line ' %\
                         ( Tab(2.0), Tab(4.4), Tab(5.9), Tab(6.5) ) )
               section.append(p)
               linesLeftOnThisPage -= numRegionHeaderLines
            #
         #
         
      # For current member
      
      #if not bAddedPageBreak:
      #   p = Paragraph( ss.ParagraphStyles.Normal )
      #   p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
      #   section.append(p)
      #
      
      try:
         os.mkdir('./output/')
      except:
         pass
      #
      try:
         os.mkdir('./output/CurrentMembersByRegion/')
      except:
         pass
      #
      
      filename = './output/CurrentMembersByRegion/CurrentMembersForRegion%d_' % (regionNum)
      filename += date_time_stamp + '.rtf'
      
      # Render and print the RTF
      DR = Renderer()                                        # From PyRTF
      DR.Write( regionDoc, file( filename, 'w' ) )
      
   # For regionNum
   
   filename = './output/CurrentMemberSummaryByRegion_' + date_time_stamp + '.rtf'
   
   # Render and print the RTF
   DR = Renderer()                                           # From PyRTF
   DR.Write( combinedDoc, file( filename, 'w' ) )
   
   #----------------------------------------------------------------------------
   # Final error count
   #
   print 'CurrentMemberReports Error count =', errorCt
   
#  CurrentMemberReports()


def ExpiredMemberReports(sortedNonmembersByRegion):
   errorCt = 0
   
   # Write the report
   combinedDoc = Document()
   
   # Margins are top, left, bottom, right
   regRptMargins = MarginsPropertySet(top=1000, left=720, bottom=720, right=720)
   
   maxPageLines          = 51
   numRegionHeaderLines  =  4
   numRegionFooterLines  =  3
   numMemberLines        =  3
   bAddedPageBreak       = False
   
   for regionNum in range(1,20):
      linesLeftOnThisPage = maxPageLines
      
      regionDoc = Document()
      
      # Create a new section for each region
      section = Section(paper=None, margins=regRptMargins, break_type=3, headery=None, footery=0, landscape=False) #, first_page_number=pageNum)
      combinedDoc.Sections.append( section )
      ss  = combinedDoc.StyleSheet
      
      regionDoc.Sections.append( section )
      
      p = Paragraph( ss.ParagraphStyles.Normal )
      p.append( TEXT( r'ICHE Expired Members by Region ', size=24, bold=True) )
      p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
      p.append( TEXT( r'\tab   %d %s \line ' % (regionNum, regionNames[regionNum - 1]), size=24, bold=True) )
      section.append(p)
      
      p = Paragraph( ss.ParagraphStyles.Normal )
      p.append( r'\pard\tx%d \tx%d \tx%d \tx%d \ulw\b\fs20 Name \tab Address \tab Phone/Email \tab Region \tab Expired\line ' %\
                ( Tab(2.0), Tab(4.4), Tab(5.9), Tab(6.5) ) )
      section.append(p)
      
      linesLeftOnThisPage -= numRegionHeaderLines
      
      expiredMemberCt = len(sortedNonmembersByRegion[regionNum])
      expiredMemberNum = 0
      for expiredMember in sortedNonmembersByRegion[regionNum]:
         expiredMemberNum += 1
         name = expiredMember.mother_l_name + ', ' + expiredMember.mother_f_name
         
         ph = expiredMember.phone_home
         if ph.strip() == '':
            ph = expiredMember.phone_work
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
         #streetParts = expiredMember.street
         #for part in streetParts:
            #if part != 'PO':
               #part.capitalize()
         ##
         #street = ''.join(streetParts)
         #street = string.capwords(expiredMember.street)
         street = expiredMember.street.strip()
         
         p = Paragraph( ss.ParagraphStyles.Normal )
         p.append( r'\fs20\tx%d \tx%d \tx%d \tx%d %s \tab %s \tab %s \tab %d \tab %s \line\tab %s, %s %s \tab %s \line ' %\
                         (Tab(2.0), Tab(4.4), Tab(5.9), Tab(6.5),
                          name, street, phone, expiredMember.region, 
                         expiredMember.membership_expires, expiredMember.city.strip(), 
                         expiredMember.state, expiredMember.zip, expiredMember.email.strip() ) )
         section.append(p)
         
         linesLeftOnThisPage -= numMemberLines
         
         bAddedPageBreak = False
         
         if linesLeftOnThisPage < 4:
            if expiredMemberNum < expiredMemberCt:            
               p = Paragraph( ss.ParagraphStyles.Normal )
               p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
               section.append(p)
               
               section.append(r'\page')
               
               linesLeftOnThisPage = maxPageLines
               bAddedPageBreak = True
            #
            
            if expiredMemberNum < expiredMemberCt: 
               p = Paragraph( ss.ParagraphStyles.Normal )
               p.append( TEXT( r'ICHE Expired Members by Region ', size=24, bold=True) )
               p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
               p.append( TEXT( r'\tab   %d %s \line ' % (regionNum, regionNames[regionNum - 1]), size=24, bold=True) )
               section.append(p)
               
               p = Paragraph( ss.ParagraphStyles.Normal )
               p.append( r'\pard\tx%d \tx%d \tx%d \tx%d \ulw\b\fs20 Name \tab Address \tab Phone \tab Region \tab Expired\line ' %\
                         ( Tab(2.2), Tab(4.4), Tab(5.9), Tab(6.5) ) )
               section.append(p)
               linesLeftOnThisPage -= numRegionHeaderLines
            #
         #
         
      # For expired member
      
      #if not bAddedPageBreak:
      #   p = Paragraph( ss.ParagraphStyles.Normal )
      #   p.append( r'\pvmrg\posyb\phpg\posxc\absw1000\fs20\qc Page \chpgn')
      #   section.append(p)
         
         #p = Paragraph( ss.ParagraphStyles.Normal )
         #p.append( TEXT( r'ICHE Expired Members by Region ', size=24, bold=True) )
         #p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
         #p.append( TEXT( r'\tab   %d %s \line ' % (regionNum, regionNames[regionNum - 1]), size=24, bold=True) )
         #section.append(p)         
      #
      
      try:
         os.mkdir('./output/')
      except:
         pass
      #
      try:
         os.mkdir('./output/ExpiredMembersByRegion/')
      except:
         pass
      #
      
      filename = './output/ExpiredMembersByRegion/ExpiredMembersForRegion%d_' % (regionNum)
      filename += date_time_stamp + '.rtf'
   
      # Render and print the RTF
      DR = Renderer()                                        # From PyRTF
      DR.Write( regionDoc, file( filename, 'w' ) )
      
   # For regionNum
   
   filename = './output/ExpiredMemberSummaryByRegion_' + date_time_stamp + '.rtf'
   
   # Render and print the RTF
   DR = Renderer()                                           # From PyRTF
   DR.Write( combinedDoc, file( filename, 'w' ) )
   
   
   #----------------------------------------------------------------------------
   # Final error count
   #
   print 'ExpiredMemberSummaryByRegionReport Error count =', errorCt
   
#  ExpiredMemberReports()


#---------------------------
# Alpha-sorted lists
#---------------------------

def CurrentMembersReportAlphaSorted(sortedMembers):
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
   p.append( TEXT( r'ICHE Current Members ', size=24, bold=True) )
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
            p.append( TEXT( r'ICHE Current Members', size=24, bold=True) )
            p.append( TEXT( r'\tx%d \tx%d \tab %s ' % (Tab(4.2), Tab(5.5), date_stamp ), size=16, bold=False) )
            #p.append( TEXT( r'\tab   %d %s \line ' % (regionNum, regionNames[regionNum - 1]), size=24, bold=True) )
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


def ExpiredMembersReportAlphaSorted(sortedMembers, rptYear):
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
   
   
   #-------------------------
   # Generate Testing Reports
   #-------------------------
   
   # Get database data
   if bCachedDb:
      pkl_file = open('cacheDb/testingRegions.pkl', 'rb')
      testingRegions = pickle.load(pkl_file)
      pkl_file.close()
   else:
      testingRegions = DbGet_TestingStudentsByRegionParent(cursor, rptYear)
      
      pkl_file = open('cacheDb/testingRegions.pkl', 'wb')
      pickle.dump(testingRegions, pkl_file)
      pkl_file.close()
   #

   TestingReports(cursor, rptYear, testingRegions)                        # Done. Includes test reports by region.
   TestingReports_Ited_Regions4and5_Only(cursor, rptYear, testingRegions) # Done
   TestCountReports(cursor, rptYear, testingRegions, bNewRet=False)       # Done
   TestCountReports(cursor, rptYear, testingRegions, bNewRet=True)        # Done
   AnswerSheetsByRegionLevelReport(cursor, rptYear, testingRegions)       # Done
   AnswerSheetsByLevelRegionReport(cursor, rptYear, testingRegions)       # Done
   #TestingMembersByRegionLabels(cursor, rptYear, testingRegions)          # TODO
   
   
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
   
   CurrentMembersReportAlphaSorted(sortedMembers)                        # Done
   CurrentMemberReports(sortedMembersByRegion)                           # Done
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
   ExpiredMemberReports(sortedNonmembersByRegion)                       # Done (Summary and by-region files)

   
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
   
   CurrentExpiredMembersReportAlphaSorted(currentExpiredMembers, rptYear)   # Done
   
   
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

