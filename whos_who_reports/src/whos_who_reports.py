#-------------------------------------------------------------------------------
#
# make_whos_who_reports.py
#
# Generates 3 reports:
#    Who's who grades 5-8
#    Who's Who grages 9-12
#    Summa / Who's Who grades 9-12
#
# Requires Python, MySqlDb.
#
# MAKE SURE THAT THE icherstest DB IS UP TO DATE!
#-------------------------------------------------------------------------------

# Python imports
from types import *
import os
import sys
import imp
import copy

# Third party imports
import MySQLdb
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

# ICHE imports
import orm
import version


def GetDbScores(test_year):

   compositeSum = vocabularySum = readingSum = languageSum = mathematicsSum = sourcesSum = 0
   studentNum = 0
   numSummedStudents = 0

   #db = MySQLdb.connect( host = "net.iche-idaho.org", user = "sugarloaf6160", 
   #							 passwd = "goldm1ning4fun", db = "ichetemp")
   db = MySQLdb.connect( host = "net.iche-idaho.org", user = "iche", 
                         passwd = "s1lvercreek", db = "icherstest")
   cursor = db.cursor()

   # Whos who reports
   # cursor.execute( "".join(['SELECT DISTINCT score_student_data.region_num, '
   #                          'score_student_data.f_name, score_student_data.l_name, '
   #                          'testing_history.summa, testing_history.whos_who, score_student_data.grade, '
   #                          'member.street, member.city, member.state, member.zip, member.phone_home, '
   #                          'score_npr.composite, student.student_id '
   #                          'FROM '
   #                          '    score_student_data, testing_history, member, student, score_npr '
   #                          'WHERE '
   #                          '    score_student_data.student_id = student.student_id '
   #                          'AND score_student_data.score_id   = score_npr.score_id '
   #                          'AND student.member_id             = member.member_id '
   #                          'AND student.student_id            = testing_history.student_id '
   #                          'AND testing_history.grade >= "5" '
   #                          'AND testing_history.test_year = "' + str(test_year) + '" '
   #                          'AND year( score_student_data.date_tested ) = "' + str(test_year) + '" '
   #                          'AND score_npr.composite >= "80" '
   #                          'LIMIT 3000 ' ] ) )
   cursor.execute("".join(['SELECT DISTINCT score_student_data.region_num, score_student_data.f_name, '
                           'score_student_data.l_name, h.summa, h.whos_who, score_student_data.grade, '
                           'm.street, m.city, m.state, m.zip, m.phone_home, '
                           'IFNULL(s.composite, i.cplte_comp_ela), t.student_id '
                           'FROM score_student_data '
                           'join student t on t.student_id = score_student_data.student_id '
                           'left join iowa_score_npr i on i.score_id = score_student_data.score_id '
                           'left join score_npr s on s.score_id = score_student_data.score_id '
                           'join testing_history h on h.student_id = score_student_data.student_id '
                           'join member m on m.member_id = t.member_id '
                           'WHERE h.test_year = ' + str(test_year) + ' '
                           'AND h.grade >= 5 '
                           'AND (s.composite >= 80 OR i.cplte_comp_ela >= 80) '
   						   'AND year(score_student_data.date_tested) = ' + str(test_year) + ' '
                           'AND score_student_data.student_id is not null '
                           'LIMIT 3000']))

   student_data = list( cursor.fetchall() )   # From tuple

   for student in student_data:
      print student

   print '########################'

   student_data.sort()   # Sorts by region, the first field

   for student in student_data:
      print student

   print
   print 'len(student_data)', len(student_data)

   #----------------------------------
   # Sort by last name within regions
   #----------------------------------
   sorted_data = []
   
   for region in range(1, 20):
      temp_data = []      
      
      for student in student_data:
         if region == student[0]:
            temp_data.append( [student[2]] + list(student) )   # Move l_name to the head to sort on
         #
      #
      
      if len(temp_data) > 0:
         # Sort just the one region's worth
         temp_data.sort()
         
         for student in temp_data:
            sorted_data.append( student[1:] )                 # Remove the l_name at the head
         #
      #
   #
   
   return  sorted_data

# End GetDbScores()


def GetDbScoresQualifiedInLast4Years(test_year):

    compositeSum = vocabularySum = readingSum = languageSum = mathematicsSum = sourcesSum = 0
    studentNum = 0
    numSummedStudents = 0

    #db = MySQLdb.connect( host = "net.iche-idaho.org", user = "sugarloaf6160",
    #							 passwd = "goldm1ning4fun", db = "ichetemp")
    db = MySQLdb.connect( host = "net.iche-idaho.org", user = "iche",
        passwd = "s1lvercreek", db = "icherstest")
    cursor = db.cursor()

    #we need to select all students that may have tested and qualified in the last 4 tests
    test_year = int(test_year) - 3

    # Whos who reports
    # cursor.execute( "".join(['SELECT DISTINCT score_student_data.region_num, '
    #                          'score_student_data.f_name, score_student_data.l_name, '
    #                          'member.street, member.city, member.state, member.zip, member.phone_home, '
    #                          'student.student_id '
    #                          'FROM '
    #                          '    score_student_data, testing_history, member, student, score_npr '
    #                          'WHERE '
    #                          '    score_student_data.student_id = student.student_id '
    #                          'AND score_student_data.score_id   = score_npr.score_id '
    #                          'AND student.member_id             = member.member_id '
    #                          'AND student.student_id            = testing_history.student_id '
    #                          'AND testing_history.grade >= "9" '
    #                          'AND testing_history.test_year >= "' + str(test_year) + '" '
    #                          'AND year( score_student_data.date_tested ) >= "' + str(test_year) + '" '
    #                         'AND score_npr.composite >= "80" '
    #                         'LIMIT 3000 ' ] ) )
    cursor.execute("".join(['SELECT DISTINCT score_student_data.region_num, score_student_data.f_name, '
                            'score_student_data.l_name, m.street, m.city, m.state, m.zip, m.phone_home, t.student_id '
                            'FROM score_student_data '
                            'join student t on t.student_id = score_student_data.student_id '
                            'left join iowa_score_npr i on i.score_id = score_student_data.score_id '
                            'left join score_npr s on s.score_id = score_student_data.score_id '
                            'join testing_history h on h.student_id = score_student_data.student_id '
                            'join member m on m.member_id = t.member_id '
                            'WHERE ((h.test_year = "' + str(test_year) + '" AND h.grade >= "9")) '
                            'AND (s.composite >= 80 OR i.cplte_comp_ela >= 80) '
                            'AND year(score_student_data.date_tested) = ' + str(test_year) + ' '
                            'AND score_student_data.student_id is not null '
                            'LIMIT 3000']))


    student_data = list( cursor.fetchall() )   # From tuple

    for student in student_data:
        print student

    print '########################'

    student_data.sort()   # Sorts by region, the first field

    for student in student_data:
        print student

    print
    print 'len(student_data)', len(student_data)

    #----------------------------------
    # Sort by last name within regions
    #----------------------------------
    sorted_data = []

    for region in range(1, 20):
        temp_data = []

        for student in student_data:
            if region == student[0]:
                temp_data.append( [student[2]] + list(student) )   # Move l_name to the head to sort on
                #
            #

        if len(temp_data) > 0:
            # Sort just the one region's worth
            temp_data.sort()

            for student in temp_data:
                sorted_data.append( student[1:] )                 # Remove the l_name at the head
                #
                #
        #

    return  sorted_data

# End GetDbScoresQualifiedInLast4Years()

def GetCompositeScoreForStudent(cursor, student_id, year, score):

    # if year < '2018':
    #     cursor.execute("".join(['SELECT DISTINCT score_student_data.region_num, '
    #                             'score_student_data.f_name, score_student_data.l_name, '
    #                             'testing_history.summa, testing_history.whos_who, score_student_data.grade, '
    #                             'member.street, member.city, member.state, member.zip, member.phone_home, score_npr.composite '
    #                             'FROM '
    #                             '    score_student_data, testing_history, member, student, score_npr '
    #                             'WHERE '
    #                             '    score_student_data.student_id = student.student_id '
    #                             'AND score_student_data.score_id = score_npr.score_id '
    #                             'AND student.member_id           = member.member_id '
    #                             'AND student.student_id = testing_history.student_id '
    #                             'AND score_student_data.student_id is not null '
    #                             'AND testing_history.grade >= "5" '
    #                             'AND testing_history.test_year = "' + str(year) + '" '
    #                             'AND year( score_student_data.date_tested ) = "' + str(year) + '" '
    #                             'AND score_npr.composite >= "' + str(score) + '" '
    #                             'AND student.student_id = "' + str(student_id) + '"'
    #                             'LIMIT 3000 ']))
    # else:
    #     cursor.execute("".join(['SELECT DISTINCT score_student_data.region_num, '
    #                             'score_student_data.f_name, score_student_data.l_name, '
    #                             'testing_history.summa, testing_history.whos_who, score_student_data.grade, '
    #                             'member.street, member.city, member.state, member.zip, member.phone_home, score_npr.cplte_comp_ela '
    #                             'FROM '
    #                             '    score_student_data, testing_history, member, student, iowa_score_npr '
    #                             'WHERE '
    #                             '    score_student_data.student_id = student.student_id '
    #                             'AND score_student_data.score_id = score_npr.score_id '
    #                             'AND student.member_id           = member.member_id '
    #                             'AND student.student_id = testing_history.student_id '
    #                             'AND score_student_data.student_id is not null '
    #                             'AND testing_history.grade >= "5" '
    #                             'AND testing_history.test_year = "' + str(year) + '" '
    #                             'AND year( score_student_data.date_tested ) = "' + str(year) + '" '
    #                             'AND score_npr.cplte_comp_ela >= "' + str(score) + '" '
    #                             'AND student.student_id = "' + str(student_id) + '"'
    #                             'LIMIT 3000 ']))

    cursor.execute("".join(['SELECT DISTINCT score_student_data.region_num, score_student_data.f_name, '
                            'score_student_data.l_name, h.summa, h.whos_who, score_student_data.grade, '
                            'm.street, m.city, m.state, m.zip, m.phone_home, ifnull(s.composite, i.cplte_comp_ela) '
                            'FROM score_student_data '
                            'join student t on t.student_id = score_student_data.student_id '
                            'left join iowa_score_npr i on i.score_id = score_student_data.score_id '
                            'left join score_npr s on s.score_id = score_student_data.score_id '
                            'join testing_history h on h.student_id = score_student_data.student_id '
                            'join member m on m.member_id = t.member_id '
                            'WHERE ((h.test_year = ' + str(year) + ' AND h.grade >= 5)) '
                            'AND (s.composite >= ' + str(score) + ' OR i.cplte_comp_ela >= ' + str(score) + ') '
                            'AND year(score_student_data.date_tested) = ' + str(year) + ' '
                            'AND score_student_data.student_id is not null '
                            'AND t.student_id = "' + str(student_id) + '"'
                            'LIMIT 3000']))

    student_data = list(cursor.fetchall())
    print student_data

    try:
        composite = student_data[0][11]
    except:
        composite = ''

    return composite
#  GetCompositeScoreForStudent()

def GetCompositeScoreAndGradeForStudent(cursor, student_id, year, score):

    # if year < '2018':
    #     cursor.execute("".join(['SELECT DISTINCT score_student_data.region_num, '
    #                             'score_student_data.f_name, score_student_data.l_name, '
    #                             'testing_history.summa, testing_history.whos_who, score_student_data.grade, '
    #                             'member.street, member.city, member.state, member.zip, member.phone_home, score_npr.composite '
    #                             'FROM score_student_data, testing_history, member, student, score_npr '
    #                             'WHERE score_student_data.student_id = student.student_id '
    #                             'AND score_student_data.score_id = score_npr.score_id '
    #                             'AND student.member_id           = member.member_id '
    #                             'AND student.student_id = testing_history.student_id '
    #                             'AND score_student_data.student_id is not null '
    #                             'AND testing_history.grade >= "5" '
    #                             'AND testing_history.test_year = "' + str(year) + '" '
    #                             'AND year( score_student_data.date_tested ) = "' + str(year) + '" '
    #                             'AND score_npr.composite >= "' + str(score) + '" '
    #                             'AND student.student_id = "' + str(student_id) + '" '
    #                             'LIMIT 3000 ']))
    # else:
    #     cursor.execute("".join(['SELECT DISTINCT score_student_data.region_num, '
    #                             'score_student_data.f_name, score_student_data.l_name, '
    #                             'testing_history.summa, testing_history.whos_who, score_student_data.grade, '
    #                             'member.street, member.city, member.state, member.zip, member.phone_home, iowa_score_npr.cplte_comp_ela '
    #                             'FROM score_student_data, testing_history, member, student, iowa_score_npr '
    #                             'WHERE score_student_data.student_id = student.student_id '
    #                             'AND score_student_data.score_id = iowa_score_npr.score_id '
    #                             'AND student.member_id           = member.member_id '
    #                             'AND student.student_id = testing_history.student_id '
    #                             'AND score_student_data.student_id is not null '
    #                             'AND testing_history.grade >= "5" '
    #                             'AND testing_history.test_year = "' + str(year) + '" '
    #                             'AND year( score_student_data.date_tested ) = "' + str(year) + '" '
    #                             'AND iowa_score_npr.cplte_comp_ela >= "' + str(score) + '" '
    #                             'AND student.student_id = "' + str(student_id) + '" '
    #                             'LIMIT 3000 ']))
    cursor.execute("".join(['SELECT DISTINCT score_student_data.region_num, score_student_data.f_name, '
                            'score_student_data.l_name, h.summa, h.whos_who, score_student_data.grade, '
                            'm.street, m.city, m.state, m.zip, m.phone_home, ifnull(s.composite, i.cplte_comp_ela) '
                            'FROM score_student_data '
                            'join student t on t.student_id = score_student_data.student_id '
                            'left join iowa_score_npr i on i.score_id = score_student_data.score_id '
                            'left join score_npr s on s.score_id = score_student_data.score_id '
                            'join testing_history h on h.student_id = score_student_data.student_id '
                            'join member m on m.member_id = t.member_id '
                            'WHERE ((h.test_year = ' + str(year) + ' AND h.grade >= 5)) '
                            'AND (s.composite >= ' + str(score) + ' OR i.cplte_comp_ela >= ' + str(score) + ') '
                            'AND year(score_student_data.date_tested) = ' + str(year) + ' '
                            'AND score_student_data.student_id is not null '
                            'AND t.student_id = "' + str(student_id) + '"'
                            'LIMIT 3000']))

    student_data = list(cursor.fetchall())
    # print student_data

    try:
        # return the composite score and the grade on that record
        # composite = str(student_data[0][11]) + " G" + str(student_data[0][5])
        composite = "G" + str(student_data[0][5])
    except:
        composite = ''

    return composite

#  GetCompositeScoreAndGradeForStudent()

def GetDbScoresQualifiedSeniorsInLast4Years(test_year):

    compositeSum = vocabularySum = readingSum = languageSum = mathematicsSum = sourcesSum = 0
    studentNum = 0
    numSummedStudents = 0

    #db = MySQLdb.connect( host = "net.iche-idaho.org", user = "sugarloaf6160",
    #							 passwd = "goldm1ning4fun", db = "ichetemp")
    db = MySQLdb.connect( host = "net.iche-idaho.org", user = "iche",
        passwd = "s1lvercreek", db = "icherstest")
    cursor = db.cursor()

    #we need to select all students that may have tested and qualified in the last 4 tests
    test_year1 = int(test_year) - 3
    test_year2 = int(test_year) - 2
    test_year3 = int(test_year) - 1

    # Whos who reports
    # cursor.execute( "".join(['SELECT DISTINCT score_student_data.region_num, '
    #                          'score_student_data.f_name, score_student_data.l_name, '
    #                          'member.street, member.city, member.state, member.zip, member.phone_home, '
    #                          'student.student_id '
    #                          'FROM '
    #                          '    score_student_data, testing_history, member, student, score_npr '
    #                          'WHERE '
    #                          '    score_student_data.student_id = student.student_id '
    #                          'AND score_student_data.score_id   = score_npr.score_id '
    #                          'AND student.member_id             = member.member_id '
    #                          'AND student.student_id            = testing_history.student_id '
    #                          'AND ((testing_history.test_year = "' + str(test_year1) + '" AND testing_history.grade = "9") '
    #                          'OR   (testing_history.test_year = "' + str(test_year2) + '" AND testing_history.grade = "10") '
    #                          'OR   (testing_history.test_year = "' + str(test_year3) + '" AND testing_history.grade = "11") '
    #                          'OR   (testing_history.test_year = "' + str(test_year) + '"  AND testing_history.grade = "12")) '
    #                          'AND year( score_student_data.date_tested ) >= "' + str(test_year1) + '" '
    #                         'AND score_npr.composite >= "80" '
    #                         'LIMIT 3000 ' ] ) )

    cursor.execute("".join(['SELECT DISTINCT score_student_data.region_num, score_student_data.f_name, '
                            'score_student_data.l_name, m.street, m.city, m.state, m.zip, m.phone_home, t.student_id '
                            'FROM score_student_data '
                            'join student t on t.student_id = score_student_data.student_id '
                            'left join iowa_score_npr i on i.score_id = score_student_data.score_id '
                            'left join score_npr s on s.score_id = score_student_data.score_id '
                            'join testing_history h on h.student_id = score_student_data.student_id '
                            'join member m on m.member_id = t.member_id '
                            'WHERE ((h.test_year = ' + str(test_year1) + ' AND h.grade = 9) '
                            'OR (h.test_year = ' + str(test_year2) + ' AND h.grade = 10) '
                            'OR (h.test_year = ' + str(test_year3) + ' AND h.grade = 11) '
                            'OR (h.test_year = ' + str(test_year) + ' AND h.grade = 12)) '
                            'AND year(score_student_data.date_tested) = ' + str(test_year) + ' '
                            'AND (s.composite >= 80 OR i.cplte_comp_ela >= 80) '
                            'AND score_student_data.student_id is not null '
                            'ORDER BY region_num, l_name, f_name '
                            'LIMIT 3000']))
    student_data = list( cursor.fetchall() )   # From tuple

    for student in student_data:
        print student

    print '########################'

    student_data.sort()   # Sorts by region, the first field

    for student in student_data:
        print student

    print
    print 'len(student_data)', len(student_data)

    #----------------------------------
    # Sort by last name within regions
    #----------------------------------
    sorted_data = []

    for region in range(1, 20):
        temp_data = []

        for student in student_data:
            if region == student[0]:
                temp_data.append( [student[2]] + list(student) )   # Move l_name to the head to sort on
                #
            #

        if len(temp_data) > 0:
            # Sort just the one region's worth
            temp_data.sort()

            for student in temp_data:
                sorted_data.append( student[1:] )                 # Remove the l_name at the head
                #
                #
        #

    return  sorted_data

# End GetDbScoresQualifiedSeniorsInLast4Years()

def MakeCvs_5_8_Who_Spreadsheet(data, test_year, outpath, outfile):

   try:
      os.makedirs(outpath)
   except:
      pass   # os.mkdirs throws if dir already exists! :(
   #

   filepath = os.path.join(outpath, outfile)
   f = open(filepath, 'w')

   f.write("ICHE Who's Who Report " + str(test_year) + ' -- Grades 5-8,,,,,,,\n')

   prev_region = ''
   ct = 0
   for student in data:
      grade = student[5]
      if grade >=5 and grade <= 8:
         if student[0] != prev_region:
            f.write('\n')
            f.write('Region, Student Name, Grade, Street, City, State, Zip, Phone\n')				
            prev_region = student[0]
         #
         phone = '(%s) %s-%s' % (student[10][0:3], student[10][3:6],student[10][6:10])
         street = student[6].replace(',', ':')
         line = '%s, %s, %s, %s, %s, %s, %s, %s\n' % \
              (student[0], student[1] + ' ' + student[2], student[5], street, student[7],
               student[8], student[9], phone)

         f.write(line)
         ct = ct + 1
      #
   #

   f.write('\n')
   f.write('%s Students' % ct)
   f.close()

   print "Generated CSV 5-8 Who Spreadsheet"

#  MakeCvs_5_8_Who_Spreadsheet()

def MakeCvs_5_8_Who_Merge_Spreadsheet(data, test_year, outpath, outfile):

    try:
        os.makedirs(outpath)
    except:
        pass   # os.mkdirs throws if dir already exists! :(
        #

    filepath = os.path.join(outpath, outfile)
    f = open(filepath, 'w')

    #f.write("ICHE Who's Who Report " + str(test_year) + ' -- Grades 5-8,,,,,,,\n')

    prev_region = ''
    ct = 0
    for student in data:
        grade = student[5]
        if grade >=5 and grade <= 8:
            #if student[0] != prev_region:
                #f.write('\n')
                #f.write('Region, Student Name, Grade, Street, City, State, Zip, Phone\n')
                #prev_region = student[0]
                #
            phone = '(%s) %s-%s' % (student[10][0:3], student[10][3:6],student[10][6:10])
            street = student[6].replace(',', ':')
            line = '%s, %s, %s, %s, %s, %s, %s, %s\n' %\
                   (student[0], student[1] + ' ' + student[2], student[5], street, student[7],
                    student[8], student[9], phone)

            f.write(line)
            ct = ct + 1
            #
        #

    f.write('\n')
    #f.write('%s Students' % ct)
    f.close()

    print "Generated CSV 5-8 Who Merge Spreadsheet"

#  MakeCvs_5_8_Who_Merge_Spreadsheet()

def MakeCvs_5_8_MultiYear_Whos_Who_Spreadsheet(data, test_year, outpath, csv_outfile):
   # m0-m3: minus 0-3
   short_test_year_m0 = str( int(test_year[2:4]) - 0)   
   short_test_year_m1 = str( int(test_year[2:4]) - 1)
   short_test_year_m2 = str( int(test_year[2:4]) - 2)
   short_test_year_m3 = str( int(test_year[2:4]) - 3)
   
   test_year_m0 = str( int(test_year) - 0)   
   test_year_m1 = str( int(test_year) - 1)
   test_year_m2 = str( int(test_year) - 2)
   test_year_m3 = str( int(test_year) - 3)
   
   try:
      os.makedirs(outpath)
   except:
      pass   # os.mkdirs throws if dir already exists! :(
   #

   filepath = os.path.join(outpath, csv_outfile)
   f = open(filepath, 'w')
   filepath_merge = os.path.join(outpath, 'Merge_WhosWho_5_8_Cert_' + test_year + '.csv')
   f_merge = open(filepath_merge, 'w')

   f.write("ICHE Multi-Year Who's Who Report " + str(test_year) + ' -- Grades 5-8,,,,,,,\n')
   f.write('\n')
   '''
   f.write(', , , SUMA, , , , WHO\'S WHO, , , , , , , ,\n')
   f.write('Region, Student Name, %s, %s, %s, %s, %s, %s, %s, %s, Grade, Street, City, State, Zip, Phone\n' %\
           (test_year_m3, test_year_m2, test_year_m1, test_year_m0,
            test_year_m3, test_year_m2, test_year_m1, test_year_m0) )
   '''
   f.write(', , , , WHO\'S WHO, , , , , , , ,\n')
   f.write('Region, Student Name, %s, %s, %s, %s, Grade, Street, City, State, Zip, Phone\n' %\
           (test_year_m3, test_year_m2, test_year_m1, test_year_m0) )
   
   db = MySQLdb.connect( host = "net.iche-idaho.org", user = "iche", 
                        passwd = "s1lvercreek", db = "icherstest")
   cursor = db.cursor()

   prev_region = ''
   ct = 0	
   bFirstPass = True
   for student in data:
      
      student_id = student[12]
      
      w_m3 = GetCompositeScoreForStudent(cursor, student_id, test_year_m3, 80)
      if w_m3 != '':
         w_m3 = 'X'
      
      w_m2 = GetCompositeScoreForStudent(cursor, student_id, test_year_m2, 80)
      if w_m2 != '':
         w_m2 = 'X'
      
      w_m1 = GetCompositeScoreForStudent(cursor, student_id, test_year_m1, 80)
      if w_m1 != '':
         w_m1 = 'X'
      
      w_m0 = GetCompositeScoreForStudent(cursor, student_id, test_year_m0, 80)
      if w_m0 != '':
         w_m0 = 'X'
      
      
      grade = student[5]
      composite = student[11]

      if grade >=5 and grade <= 8 and composite >= 80:
         if (student[0] != prev_region) and not bFirstPass:
            f.write('\n')
            f.write('Region, Student Name, W%s, W%s, W%s, W%s, Grade, Street, City, State, Zip, Phone\n' %\
                    (short_test_year_m3, short_test_year_m2, short_test_year_m1, short_test_year_m0) )				
         #
         prev_region = student[0]         
         bFirstPass = False         
         
         phone = '(%s) %s-%s' % (student[10][0:3], student[10][3:6],student[10][6:10])
         street = student[6].replace(',', ':')
         
         line = '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n' % \
              (student[0], student[1] + ' ' + student[2], 
               w_m3, w_m2, w_m1, w_m0, student[5], street, student[7],
               student[8], student[9], phone)

         if w_m0 == 'X' and w_m1 == '' and w_m2 == '' and w_m3 == '':
             f_merge.write(line)
         f.write(line)
         ct = ct + 1			
      #
   #

   f.write('\n')
   f.write('%s Students' % ct)
   f_merge.write('\n')
   f.close()
   f_merge.close()

   print "Generated CSV 5-8 MultiYear Whos Who Spreadsheet"
   
# MakeCvs_5_8_MultiYear_Whos_Who_Spreadsheet()

def MakeCvs_9_12_Who_Spreadsheet(data, test_year, outpath, outfile):

   try:
      os.makedirs(outpath)
   except:
      pass   # os.mkdirs throws if dir already exists! :(
   #

   filepath = os.path.join(outpath, outfile)
   f = open(filepath, 'w')

   f.write("ICHE Who's Who Report " + str(test_year) + ' -- Grades 9-12,,,,,,,\n')

   prev_region = ''
   ct = 0	
   for student in data:
      grade = student[5]
      if grade >=9 and grade <= 12:
         if student[0] != prev_region:
            f.write('\n')
            f.write('Region, Student Name, Grade, Street, City, State, Zip, Phone\n')				
            prev_region = student[0]
         #
         phone = '(%s) %s-%s' % (student[10][0:3], student[10][3:6],student[10][6:10])
         street = student[6].replace(',', ':')
         line = '%s, %s, %s, %s, %s, %s, %s, %s\n' % \
              (student[0], student[1] + ' ' + student[2], student[5], street, student[7],
               student[8], student[9], phone)

         f.write(line)
         ct = ct + 1			
      #
   #

   f.write('\n')
   f.write('%s Students' % ct)
   f.close()

   print "Generated CSV 9-12 Who Spreadsheet"

#  MakeCvs_9_12_Who_Spreadsheet()

def MakeCvs_9_12_Who_Merge_Spreadsheet(data, test_year, outpath, outfile):

    try:
        os.makedirs(outpath)
    except:
        pass   # os.mkdirs throws if dir already exists! :(
        #

    filepath = os.path.join(outpath, outfile)
    f = open(filepath, 'w')

    #f.write("ICHE Who's Who Report " + str(test_year) + ' -- Grades 9-12,,,,,,,\n')

    prev_region = ''
    ct = 0
    for student in data:
        grade = student[5]
        if grade >=9 and grade <= 12:
            #if student[0] != prev_region:
                #f.write('\n')
                #f.write('Region, Student Name, Grade, Street, City, State, Zip, Phone\n')
                #prev_region = student[0]
                #
            phone = '(%s) %s-%s' % (student[10][0:3], student[10][3:6],student[10][6:10])
            street = student[6].replace(',', ':')
            line = '%s, %s, %s, %s, %s, %s, %s, %s\n' %\
                   (student[0], student[1] + ' ' + student[2], student[5], street, student[7],
                    student[8], student[9], phone)

            f.write(line)
            ct = ct + 1
            #
        #

    f.write('\n')
    #f.write('%s Students' % ct)
    f.close()

    print "Generated CSV 9-12 Who Merge Spreadsheet"

#  MakeCvs_9_12_Who_Merge_Spreadsheet()



def MakeCvs_9_12_Summa_Who_Spreadsheet(data, test_year, outpath, outfile):

   short_test_year_m0 = str( int(test_year[2:4]) - 0)   
   short_test_year_m1 = str( int(test_year[2:4]) - 1)
   short_test_year_m2 = str( int(test_year[2:4]) - 2)
   short_test_year_m3 = str( int(test_year[2:4]) - 3)
   
   test_year_m0 = str( int(test_year) - 0)   
   test_year_m1 = str( int(test_year) - 1)
   test_year_m2 = str( int(test_year) - 2)
   test_year_m3 = str( int(test_year) - 3)
   
   try:
      os.makedirs(outpath)
   except:
      pass   # os.mkdirs throws if dir already exists! :(
   #

   filepath = os.path.join(outpath, outfile)
   f = open(filepath, 'w')
   filepath_merge = os.path.join(outpath, 'Merge_Summa_9_12_Cert_' + test_year + '.csv')
   f_merge = open(filepath_merge, 'w')
   filepath_merge2 = os.path.join(outpath, 'Merge_WhosWho_9_12_Cert_' + test_year + '.csv')
   f_merge2 = open(filepath_merge2, 'w')
   filepath_merge3 = os.path.join(outpath, 'MergeLetter_9_12_Summa_' + test_year + '.csv')
   f_merge3 = open(filepath_merge3, 'w')

   f.write("ICHE Summa Report " + str(test_year) + ' -- Grades 9-12,,,,,,,\n')
   f.write('\n')
   f.write(', , , SUMA, , , , WHO\'S WHO, , , , , , , ,\n')
   f.write('Region, Student Name, %s, %s, %s, %s, %s, %s, %s, %s, Grade, Street, City, State, Zip, Phone\n' %\
           (test_year_m3, test_year_m2, test_year_m1, test_year_m0,
            test_year_m3, test_year_m2, test_year_m1, test_year_m0) )
   f_merge.write('Region, Student Name, %s, %s, %s, %s, %s, %s, %s, %s, Grade, Street, City, State, Zip, Phone\n' %\
            (test_year_m3, test_year_m2, test_year_m1, test_year_m0,
             test_year_m3, test_year_m2, test_year_m1, test_year_m0) )
   f_merge2.write('Region, Student Name, %s, %s, %s, %s, %s, %s, %s, %s, Grade, Street, City, State, Zip, Phone\n' %\
            (test_year_m3, test_year_m2, test_year_m1, test_year_m0,
             test_year_m3, test_year_m2, test_year_m1, test_year_m0) )


   db = MySQLdb.connect( host = "net.iche-idaho.org", user = "iche", passwd = "s1lvercreek", db = "icherstest")
   cursor = db.cursor()

   prev_region = ''
   ct = 0	
   bFirstPass = True
   for student in data:
      
      student_id = student[12]
  
      s_m3 = GetCompositeScoreForStudent(cursor, student_id, test_year_m3, 90)
      if s_m3 != '':
         s_m3 = 'X'
      
      s_m2 = GetCompositeScoreForStudent(cursor, student_id, test_year_m2, 90)
      if s_m2 != '':
         s_m2 = 'X'
      
      s_m1 = GetCompositeScoreForStudent(cursor, student_id, test_year_m1, 90)
      if s_m1 != '':
         s_m1 = 'X'
      
      s_m0 = GetCompositeScoreForStudent(cursor, student_id, test_year_m0, 90)
      if s_m0 != '':
         s_m0 = 'X'
      
      
      w_m3 = GetCompositeScoreForStudent(cursor, student_id, test_year_m3, 80)
      if w_m3 != '':
         w_m3 = 'X'
      
      w_m2 = GetCompositeScoreForStudent(cursor, student_id, test_year_m2, 80)
      if w_m2 != '':
         w_m2 = 'X'
      
      w_m1 = GetCompositeScoreForStudent(cursor, student_id, test_year_m1, 80)
      if w_m1 != '':
         w_m1 = 'X'
      
      w_m0 = GetCompositeScoreForStudent(cursor, student_id, test_year_m0, 80)
      if w_m0 != '':
         w_m0 = 'X'
      
      
      grade = student[5]
      composite = student[11]

      if grade >=9 and grade <= 12 and composite >= 80:
         if (student[0] != prev_region) and not bFirstPass:
            f.write('\n')
            f.write('Region, Student Name, S%s, S%s, S%s, S%s, W%s, W%s, W%s, W%s, Grade, Street, City, State, Zip, Phone\n' %\
                    (short_test_year_m3, short_test_year_m2, short_test_year_m1, short_test_year_m0,
                     short_test_year_m3, short_test_year_m2, short_test_year_m1, short_test_year_m0) )				
         #
         prev_region = student[0]         
         bFirstPass = False         
         
         phone = '(%s) %s-%s' % (student[10][0:3], student[10][3:6],student[10][6:10])
         street = student[6].replace(',', ':')
         
         line = '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n' % (student[0], student[1] + ' ' + student[2], s_m3, s_m2, s_m1, s_m0,w_m3, w_m2, w_m1, w_m0, student[5], street, student[7],student[8], student[9], phone)

         # print out to the merge file if the composite is >= 90
         if isNeedsCertificate(s_m0, s_m1, s_m2, s_m3, grade):
             f_merge.write(line)
         # output all summas to this file
         if s_m0 == 'X':
             f_merge3.write(line)
         # print out to the merge file if the composite is >= 80
         if isNeedsCertificate(w_m0, w_m1, w_m2, w_m3, grade):
             f_merge2.write(line)
         f.write(line)
         ct = ct + 1			
      #
   #

   f.write('\n')
   f.write('%s Students' % ct)
   f.close()

   f_merge.write('\n')
   f_merge.close()

   f_merge2.write('\n')
   f_merge2.close()


   print "Generated CSV 9-12 Sunmma Who Spreadsheet"

#  MakeCvs_9_12_Summa_Who_Spreadsheet()

def MakeCvs_12_All_Summa_Who_Spreadsheet(data, test_year, outpath, outfile):

    short_test_year_m0 = str( int(test_year[2:4]) - 0)
    short_test_year_m1 = str( int(test_year[2:4]) - 1)
    short_test_year_m2 = str( int(test_year[2:4]) - 2)
    short_test_year_m3 = str( int(test_year[2:4]) - 3)

    test_year_m0 = str( int(test_year) - 0)
    test_year_m1 = str( int(test_year) - 1)
    test_year_m2 = str( int(test_year) - 2)
    test_year_m3 = str( int(test_year) - 3)

    try:
        os.makedirs(outpath)
    except:
        pass   # os.mkdirs throws if dir already exists! :(
        #
    filepath = os.path.join(outpath, outfile)
    f = open(filepath, 'w')

    f.write("ICHE Summa and Who's Who Report " + str(test_year) + ' -- Grades 9-12 ALL,,,,,,,\n')
    f.write('\n')
    #f.write(', , , SUMA, , , , WHO\'S WHO, , , , , , , ,\n')
    f.write('Region, Student Name, Summa %s, Summa %s, Summa %s, Summa %s, WHOSWHO %s, WHOSWHO %s, WHOSWHO %s, WHOSWHO %s, Street, City, State, Zip, Phone\n' %\
            (test_year_m3, test_year_m2, test_year_m1, test_year_m0,
             test_year_m3, test_year_m2, test_year_m1, test_year_m0) )

    db = MySQLdb.connect( host = "net.iche-idaho.org", user = "iche", passwd = "s1lvercreek", db = "icherstest")
    cursor = db.cursor()

    ct = 0
    for student in data:
        # grab the student id for queries
        student_id = student[8]

        #summa
        s_m3 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m3, 90)

        s_m2 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m2, 90)

        s_m1 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m1, 90)

        s_m0 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m0, 90)

        #whos who
        w_m3 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m3, 80)

        w_m2 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m2, 80)

        w_m1 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m1, 80)

        w_m0 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m0, 80)

        phone = '(%s) %s-%s' % (student[7][0:3], student[7][3:6],student[7][6:10])
        street = student[3].replace(',', ':')

        line = '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n' % (student[0], student[1] + ' ' + student[2], s_m3, s_m2, s_m1, s_m0,w_m3, w_m2, w_m1, w_m0, street, student[4],student[5], student[6], phone)
        print line
        f.write(line)
        ct = ct + 1
        #

    f.write('\n')
    f.write('%s Students' % ct)
    f.close()

    print "Generated CSV 9-12 ALL Summa Who Spreadsheet"

#  MakeCvs_12_All_Summa_Who_Spreadsheet()

# check the whos who or summa for 9-12
def isNeedsCertificate(m0, m1, m2, m3, grade):
    if grade == 12:
        if m0 == 'X' and m1 == '' and m2 == '' and m3 == '':
            return True
    if grade == 11:
        if m0 == 'X' and m1 == '' and m2 == '':
            return True
    if grade == 10:
        if m0 == 'X' and m1 == '':
            return True
    if grade == 9:
        if m0 == 'X':
            return True
# isNeedsCertificate

#  MakeCvs_12_Seniors_Summa_Who_Spreadsheet()

def MakeCvs_12_Seniors_Summa_Who_Spreadsheet(data, test_year, outpath, outfile):

    short_test_year_m0 = str( int(test_year[2:4]) - 0)
    short_test_year_m1 = str( int(test_year[2:4]) - 1)
    short_test_year_m2 = str( int(test_year[2:4]) - 2)
    short_test_year_m3 = str( int(test_year[2:4]) - 3)

    test_year_m0 = str( int(test_year) - 0)
    test_year_m1 = str( int(test_year) - 1)
    test_year_m2 = str( int(test_year) - 2)
    test_year_m3 = str( int(test_year) - 3)

    try:
        os.makedirs(outpath)
    except:
        pass   # os.mkdirs throws if dir already exists! :(
        #
    filepath = os.path.join(outpath, outfile)
    f = open(filepath, 'w')

    f.write("ICHE Summa and Who's Who Report " + str(test_year) + ' -- Grades 12,,,,,,,\n')
    f.write('\n')
    #f.write(', , , SUMA, , , , WHO\'S WHO, , , , , , , ,\n')
    f.write('Region, Student Name, Summa %s, Summa %s, Summa %s, Summa %s, WHOSWHO %s, WHOSWHO %s, WHOSWHO %s, WHOSWHO %s, Street, City, State, Zip, Phone\n' %\
            (test_year_m3, test_year_m2, test_year_m1, test_year_m0,
             test_year_m3, test_year_m2, test_year_m1, test_year_m0) )

    db = MySQLdb.connect( host = "net.iche-idaho.org", user = "iche", passwd = "s1lvercreek", db = "icherstest")
    cursor = db.cursor()

    ct = 0
    for student in data:
        # grab the student id for queries
        student_id = student[8]

        #summa
        s_m3 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m3, 90)

        s_m2 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m2, 90)

        s_m1 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m1, 90)

        s_m0 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m0, 90)

        #whos who
        w_m3 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m3, 80)

        w_m2 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m2, 80)

        w_m1 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m1, 80)

        w_m0 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m0, 80)

        phone = '(%s) %s-%s' % (student[7][0:3], student[7][3:6],student[7][6:10])
        street = student[3].replace(',', ':')

        line = '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n' % (student[0], student[1] + ' ' + student[2], s_m3, s_m2, s_m1, s_m0,w_m3, w_m2, w_m1, w_m0, street, student[4],student[5], student[6], phone)
        print line
        f.write(line)
        ct = ct + 1
        #

    f.write('\n')
    f.write('%s Students' % ct)
    f.close()

    print "Generated CSV 12 Seniors Summa Who Spreadsheet"

#---------------------------------------------------------------------------------------------------
#  Main routine for generating who's who reports
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   '''
	Program starts here. Expects the test year as the only argument.
	'''
   print 'whos_who_reports v' + version.version

   test_year = sys.argv[1]

   print 'generating reports for test year: ' + test_year

   outpath = './output/'

   #if False:   #used for testing the last report at the bottom (commenting out the rest)
   data = GetDbScores(test_year)

   print 'got student data'

   csv_outfile = 'ICHE_5_8_Whos_Who_Report_' + test_year + '.csv'
   MakeCvs_5_8_Who_Spreadsheet(data, test_year, outpath, csv_outfile)

   csv_outfile = 'MergeLetter_ICHE_5_8_Whos_Who_' + test_year + '.csv'
   MakeCvs_5_8_Who_Merge_Spreadsheet(data, test_year, outpath, csv_outfile)

   csv_outfile = 'ICHE_5_8_MultiYear_Whos_Who_Report_' + test_year + '.csv'
   MakeCvs_5_8_MultiYear_Whos_Who_Spreadsheet(data, test_year, outpath, csv_outfile)

   csv_outfile = 'ICHE_9_12_Whos_Who_Report_' + test_year + '.csv'
   MakeCvs_9_12_Who_Spreadsheet(data, test_year, outpath, csv_outfile)

   csv_outfile = 'MergeLetter_ICHE_9_12_Whos_Who_' + test_year + '.csv'
   MakeCvs_9_12_Who_Merge_Spreadsheet(data, test_year, outpath, csv_outfile)

   csv_outfile = 'ICHE_9_12_Summa_Who_Report_' + test_year + '.csv'
   MakeCvs_9_12_Summa_Who_Spreadsheet(data, test_year, outpath, csv_outfile)

   # new in 2013 for sending to graduation committee, this report queries all students
   # who qualified in the last 4 years and lists them by region
   csv_outfile = 'ICHE_12_Summa_Who_Report_Graduation_' + test_year + '.csv'
   grad_data = GetDbScoresQualifiedInLast4Years(test_year)
   MakeCvs_12_All_Summa_Who_Spreadsheet(grad_data, test_year, outpath, csv_outfile)

   # new in 2016 for checking honor chords
   csv_outfile = 'ICHE_12_Summa_Who_Report_Graduation_Seniors_' + test_year + '.csv'
   senior_data = GetDbScoresQualifiedSeniorsInLast4Years(test_year)
   MakeCvs_12_Seniors_Summa_Who_Spreadsheet(senior_data, test_year, outpath, csv_outfile)

   # Display the newly-generated .csv!
   #os.chdir(outpath)
   #os.system(csv_outfile)

   print 'All done generating whos who and summa reports for ' + str(test_year)
# End main

# EOF

