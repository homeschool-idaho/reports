# -------------------------------------------------------------------------------
#
# make_whos_who_reports.py
#
# Generates 1 report:
#    Summa / Who's Who grade 12
#
# Requires Python, MySqlDb.
#
# MAKE SURE THAT THE icherstest DB IS UP TO DATE!
# -------------------------------------------------------------------------------

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




def GetCompositeScoreForStudent(cursor, student_id, year, score):

    if year < '2018':
        cursor.execute("".join(['SELECT DISTINCT score_student_data.region_num, '
                                'score_student_data.f_name, score_student_data.l_name, '
                                'testing_history.summa, testing_history.whos_who, score_student_data.grade, '
                                'member.street, member.city, member.state, member.zip, member.phone_home, score_npr.composite '
                                'FROM '
                                '    score_student_data, testing_history, member, student, score_npr '
                                'WHERE '
                                '    score_student_data.student_id = student.student_id '
                                'AND score_student_data.score_id = score_npr.score_id '
                                'AND student.member_id           = member.member_id '
                                'AND student.student_id = testing_history.student_id '
                                'AND score_student_data.student_id is not null '
                                'AND testing_history.grade >= "5" '
                                'AND testing_history.test_year = "' + str(year) + '" '
                                'AND year( score_student_data.date_tested ) = "' + str(year) + '" '
                                'AND score_npr.composite >= "' + str(score) + '" '
                                'AND student.student_id = "' + str(student_id) + '"'
                                'LIMIT 3000 ']))
    else:
        cursor.execute("".join(['SELECT DISTINCT score_student_data.region_num, '
                                'score_student_data.f_name, score_student_data.l_name, '
                                'testing_history.summa, testing_history.whos_who, score_student_data.grade, '
                                'member.street, member.city, member.state, member.zip, member.phone_home, score_npr.cplte_comp_ela '
                                'FROM '
                                '    score_student_data, testing_history, member, student, iowa_score_npr '
                                'WHERE '
                                '    score_student_data.student_id = student.student_id '
                                'AND score_student_data.score_id = score_npr.score_id '
                                'AND student.member_id           = member.member_id '
                                'AND student.student_id = testing_history.student_id '
                                'AND score_student_data.student_id is not null '
                                'AND testing_history.grade >= "5" '
                                'AND testing_history.test_year = "' + str(year) + '" '
                                'AND year( score_student_data.date_tested ) = "' + str(year) + '" '
                                'AND score_npr.cplte_comp_ela >= "' + str(score) + '" '
                                'AND student.student_id = "' + str(student_id) + '"'                                                                                             
                                'LIMIT 3000 ']))

    student_data = list(cursor.fetchall())
    print student_data

    try:
        composite = student_data[0][11]
    except:
        composite = ''

    return composite
#  GetCompositeScoreForStudent()

def GetCompositeScoreAndGradeForStudent(cursor, student_id, year, score):

    if year < '2018':
        cursor.execute("".join(['SELECT DISTINCT score_student_data.region_num, '
                                'score_student_data.f_name, score_student_data.l_name, '
                                'testing_history.summa, testing_history.whos_who, score_student_data.grade, '
                                'member.street, member.city, member.state, member.zip, member.phone_home, score_npr.composite '
                                'FROM score_student_data, testing_history, member, student, score_npr '
                                'WHERE score_student_data.student_id = student.student_id '
                                'AND score_student_data.score_id = score_npr.score_id '
                                'AND student.member_id           = member.member_id '
                                'AND student.student_id = testing_history.student_id '
                                'AND score_student_data.student_id is not null '
                                'AND testing_history.grade >= "5" '
                                'AND testing_history.test_year = "' + str(year) + '" '
                                'AND year( score_student_data.date_tested ) = "' + str(year) + '" '
                                'AND score_npr.composite >= "' + str(score) + '" '
                                'AND student.student_id = "' + str(student_id) + '" '
                                'LIMIT 3000 ']))
    else:
        cursor.execute("".join(['SELECT DISTINCT score_student_data.region_num, '
                                'score_student_data.f_name, score_student_data.l_name, '
                                'testing_history.summa, testing_history.whos_who, score_student_data.grade, '
                                'member.street, member.city, member.state, member.zip, member.phone_home, iowa_score_npr.cplte_comp_ela '
                                'FROM score_student_data, testing_history, member, student, iowa_score_npr '
                                'WHERE score_student_data.student_id = student.student_id '
                                'AND score_student_data.score_id = iowa_score_npr.score_id '
                                'AND student.member_id           = member.member_id '
                                'AND student.student_id = testing_history.student_id '
                                'AND score_student_data.student_id is not null '
                                'AND testing_history.grade >= "5" '
                                'AND testing_history.test_year = "' + str(year) + '" '
                                'AND year( score_student_data.date_tested ) = "' + str(year) + '" '
                                'AND iowa_score_npr.cplte_comp_ela >= "' + str(score) + '" '
                                'AND student.student_id = "' + str(student_id) + '" '
                                'LIMIT 3000 ']))

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

def GetDbScoresQualifiedSeniorsInLastYear(test_year, current_year):
    compositeSum = vocabularySum = readingSum = languageSum = mathematicsSum = sourcesSum = 0
    studentNum = 0
    numSummedStudents = 0

    # db = MySQLdb.connect( host = "net.iche-idaho.org", user = "sugarloaf6160",
    #							 passwd = "goldm1ning4fun", db = "ichetemp")
    db = MySQLdb.connect(host="net.iche-idaho.org", user="iche",
                         passwd="s1lvercreek", db="icherstest")
    cursor = db.cursor()

    grade = '" AND h.grade = "12")) '
    if test_year != current_year:
        grade = '" AND h.grade = "11")) '
        print 'test year does not match, grabbing juniors'
    # Whos who reports
    cursor.execute("".join(['SELECT DISTINCT score_student_data.region_num, score_student_data.f_name, '
                            'score_student_data.l_name, m.street, m.city, m.state, m.zip, m.phone_home, t.student_id '
                            'FROM score_student_data '
                            'join student t on t.student_id = score_student_data.student_id '
                            'left join iowa_score_npr i on i.score_id = score_student_data.score_id '
                            'left join score_npr s on s.score_id = score_student_data.score_id '
                            'join testing_history h on h.student_id = score_student_data.student_id '
                            'join member m on m.member_id = t.member_id '
                            'WHERE ((h.test_year = "' + str(test_year) + grade + ''
                            'AND (s.composite >= 80 OR i.cplte_comp_ela >= 80) '
                            'AND score_student_data.student_id is not null '
                            'LIMIT 3000']))


    student_data = list(cursor.fetchall())  # From tuple

    for student in student_data:
        print student

    print '########################'

    student_data.sort()  # Sorts by region, the first field

    for student in student_data:
        print student

    print
    print 'len(student_data)', len(student_data)

    # ----------------------------------
    # Sort by last name within regions
    # ----------------------------------
    sorted_data = []

    for region in range(1, 20):
        temp_data = []

        for student in student_data:
            if region == student[0]:
                temp_data.append([student[2]] + list(student))  # Move l_name to the head to sort on
                #
                #

        if len(temp_data) > 0:
            # Sort just the one region's worth
            temp_data.sort()

            for student in temp_data:
                sorted_data.append(student[1:])  # Remove the l_name at the head
                #
                #
                #

    return sorted_data

# End GetDbScoresQualifiedSeniorsInLast4Years()

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

def MakeCvs_12_Seniors_Summa_Who_Spreadsheet(data, test_year, outpath, outfile):
    short_test_year_m0 = str(int(test_year[2:4]) - 0)
    short_test_year_m1 = str(int(test_year[2:4]) - 1)
    short_test_year_m2 = str(int(test_year[2:4]) - 2)
    short_test_year_m3 = str(int(test_year[2:4]) - 3)

    test_year_m0 = str(int(test_year) - 0)
    test_year_m1 = str(int(test_year) - 1)
    test_year_m2 = str(int(test_year) - 2)
    test_year_m3 = str(int(test_year) - 3)

    try:
        os.makedirs(outpath)
    except:
        pass  # os.mkdirs throws if dir already exists! :(
        #
    filepath = os.path.join(outpath, outfile)
    f = open(filepath, 'w')

    f.write("ICHE Summa and Who's Who Report " + str(test_year) + ' -- Grades 12,,,,,,,\n')
    f.write('\n')
    # f.write(', , , SUMA, , , , WHO\'S WHO, , , , , , , ,\n')
    f.write(
        'Region, Student Name, Summa %s, Summa %s, Summa %s, Summa %s, WHOSWHO %s, WHOSWHO %s, WHOSWHO %s, WHOSWHO %s, Street, City, State, Zip, Phone\n' % \
        (test_year_m3, test_year_m2, test_year_m1, test_year_m0,
         test_year_m3, test_year_m2, test_year_m1, test_year_m0))

    db = MySQLdb.connect(host="net.iche-idaho.org", user="iche", passwd="s1lvercreek", db="icherstest")
    cursor = db.cursor()

    ct = 0
    for student in data:
        # grab the student id for queries
        student_id = student[8]

        # summa
        s_m3 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m3, 90)

        s_m2 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m2, 90)

        s_m1 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m1, 90)

        s_m0 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m0, 90)

        # whos who
        w_m3 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m3, 80)

        w_m2 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m2, 80)

        w_m1 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m1, 80)

        w_m0 = GetCompositeScoreAndGradeForStudent(cursor, student_id, test_year_m0, 80)

        phone = '(%s) %s-%s' % (student[7][0:3], student[7][3:6], student[7][6:10])
        street = student[3].replace(',', ':')

        line = '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n' % (
        student[0], student[1] + ' ' + student[2], s_m3, s_m2, s_m1, s_m0, w_m3, w_m2, w_m1, w_m0, street, student[4],
        student[5], student[6], phone)
        print line
        f.write(line)
        ct = ct + 1
        #

    f.write('\n')
    f.write('%s Students' % ct)
    f.close()

    print "Generated CSV 12 Seniors Summa Who Spreadsheet"

#  MakeCvs_12_Seniors_Summa_Who_Spreadsheet()

# ---------------------------------------------------------------------------------------------------
#  Main routine for generating who's who reports
# ---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    '''
     Program starts here. Expects the test year as the only argument.
     '''
    print 'gradreport v' + version.version

    test_year = sys.argv[1]
    current_year = sys.argv[2]

    print 'generating reports for test year: ' + test_year

    outpath = './output/'

    # new in 2016 for checking honor chords
    csv_outfile = 'ICHE_12_Summa_Who_Report_Graduation_Seniors_CurrentYear' + test_year + '.csv'
    senior_data = GetDbScoresQualifiedSeniorsInLastYear(test_year, current_year)
    MakeCvs_12_Seniors_Summa_Who_Spreadsheet(senior_data, test_year, outpath, csv_outfile)

    # Display the newly-generated .csv!
    # os.chdir(outpath)
    # os.system(csv_outfile)

    print 'All done generating whos who and summa reports for ' + str(test_year)
# End main

# EOF

