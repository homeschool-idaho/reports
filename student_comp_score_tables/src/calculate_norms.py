#-------------------------------------------------------------------------------
#
# calculate_norms.py
#
# Requires Python, MySqlDb.
#
# MAKE SURE THAT THE icherstest DB IS UP TO DATE!
#
# based on make_tables.py, modified to calculate norms across grade levels
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


def MedianScore(inlist):
    """
   Returns the 'middle' score of the passed list. If there is an even number of scores,
    the mean of the 2 middle scores is returned.
   """
    newlist = copy.deepcopy(inlist)
    newlist.sort()

    if len(newlist) % 2 == 0:   # If even number of scores, average the middle 2
        index = len(newlist)/2   # Integer division is correct
        median = float(newlist[index] + newlist[index-1]) / 2.0
    else:
        index = len(newlist)/2   # Integer divsion gives mid value when count starts at 0
        median = newlist[index] * 1.0
    #

    return median
# 


def GetDbScores(grades, test_year):

    compositeSum = vocabularySum = readingSum = languageSum = mathematicsSum = sourcesSum = 0
    studentNum = 0
    numSummedStudents = 0

    db = MySQLdb.connect( host = "net.iche-idaho.org", user = "iche",
                                 passwd = "s1lvercreek", db = "icherstest")

    cursor = db.cursor()

    cursor.execute("SELECT DISTINCT * from score_student_data where member_id is not null limit 0, 6000")

    student_data = cursor.fetchall()

    cur_year_students = []
    for row in student_data:
        student = orm.score_student_data(row)
        if student.date_tested.split('-')[0] != test_year:
            continue
        else:
            cur_year_students.append(student)
        #
    #

    averages = {}
    medians  = {}
    numSummedStudents = {}

    for grade in grades:
        exec 'compositeSum_' + grade +   ' = 0'
        exec 'vocabularySum_' + grade +  ' = 0'
        exec 'readingSum_' + grade +     ' = 0'
        exec 'languageSum_' + grade +    ' = 0'
        exec 'sourcesSum_' + grade +     ' = 0'
        exec 'mathematicsSum_' + grade + ' = 0'

        exec 'compositeList_' + grade +   ' = []'
        exec 'vocabularyList_' + grade +  ' = []'
        exec 'readingList_' + grade +     ' = []'
        exec 'languageList_' + grade +    ' = []'
        exec 'sourcesList_' + grade +     ' = []'
        exec 'mathematicsList_' + grade + ' = []'

        exec "numSummedStudents['" + grade + "'] = 0"
        exec "averages['" + grade + "'] = {}"
        exec "medians['" + grade + "'] = {}"
    #

    numTotalStudents = len (cur_year_students)
    studentNum = 0

    for student in cur_year_students:

        cmd = "SELECT DISTINCT * from score_npr, score_student_data where score_npr.score_id = \"" + str(student.score_id) +\
             "\" and score_npr.score_id = score_student_data.score_id and year(score_student_data.date_tested) = \"" +\
             test_year + "\" limit 0, 6000"
        #print cmd   # DEBUG
        try:
            cursor.execute(cmd)
        except Exception, e:
            print str(e)
        #
        score_npr_data = cursor.fetchall()

        stu_grade = str(student.grade)

        for srow in score_npr_data:
            if student.test_type == 'ITBS':
                score_npr    = orm.itbs_score_data(srow)
                lang_name    = 'language_total'
                sources_name = 'sources_total'

            else:
                score_npr    = orm.ited_score_data(srow)
                lang_name    = 'revise_writ_mtrl'
                sources_name = 'sources_of_info'
            #

            for grade in grades:
                if stu_grade in grade:
                    exec 'compositeSum_' + grade +   ' += score_npr.composite_pComput'
                    exec 'vocabularySum_' + grade +  ' += score_npr.vocabulary'
                    exec 'readingSum_' + grade +     ' += score_npr.reading_total'
                    exec 'languageSum_' + grade +    ' += score_npr.' + lang_name
                    exec 'sourcesSum_' + grade +     ' += score_npr.' + sources_name
                    exec 'mathematicsSum_' + grade + ' += score_npr.mathT_pComput'

                    exec 'compositeList_' + grade +   '.append(score_npr.composite_pComput)'
                    exec 'vocabularyList_' + grade +  '.append(score_npr.vocabulary)'
                    exec 'readingList_' + grade +     '.append(score_npr.reading_total)'
                    exec 'languageList_' + grade +    '.append(score_npr.' + lang_name + ')'
                    exec 'sourcesList_' + grade +     '.append(score_npr.' + sources_name + ')'
                    exec 'mathematicsList_' + grade + '.append(score_npr.mathT_pComput)'

                    exec "numSummedStudents['" + grade + "'] += 1"
                    #print "adding 1 grade", grade

                exec "numSummedStudents['All'] += 1"
                #
            #
        #

        studentNum += 1
        print "Processed student", studentNum, "of", numTotalStudents
    #

    for grade in grades:

        # Average or Arithmetic Mean: The value obtained by dividing the sum of a set of quantities by the number of quantities in the set
        averages[grade]['composite']   = eval ('compositeSum_' + grade + " / float(numSummedStudents['" + grade + "'])")
        averages[grade]['vocabulary']  = eval ('vocabularySum_' + grade + " / float(numSummedStudents['" + grade + "'])")
        averages[grade]['reading']     = eval ('readingSum_' + grade + " / float(numSummedStudents['" + grade + "'])")
        averages[grade]['language']    = eval ('languageSum_' + grade + " / float(numSummedStudents['" + grade + "'])")
        averages[grade]['sources']     = eval ('sourcesSum_' + grade + " / float(numSummedStudents['" + grade + "'])")
        averages[grade]['mathematics'] = eval ('mathematicsSum_' + grade + " / float(numSummedStudents['" + grade + "'])")

        # Median: The middle value of an ordered set of values (or the average of the middle two in a set with an even number
        medians[grade]['composite']   = eval ('MedianScore(compositeList_' + grade + ')')
        medians[grade]['vocabulary']  = eval ('MedianScore(vocabularyList_' + grade + ')')
        medians[grade]['reading']     = eval ('MedianScore(readingList_' + grade + ')')
        medians[grade]['language']    = eval ('MedianScore(languageList_' + grade + ')')
        medians[grade]['sources']     = eval ('MedianScore(sourcesList_' + grade + ')')
        medians[grade]['mathematics'] = eval ('MedianScore(mathematicsList_' + grade + ')')
    #

    return averages, medians, numSummedStudents

# End GetDbScores()


# Example:
'''
ICHE Test Results 2009,,,,,,,,,,,,,,,,,,,,,,,,,,

,,,Composite,,,Vocabulary,,,Reading,,,Language,,,Sources,,,Mathematics,,,,,,,,
Campus,#Stu,,Avg.,Med.,,Avg.,Med.,,Avg.,Med.,,Avg.,Med.,,Avg.,Med.,,Avg.,Med.,,  , , , , , 
All,549,,78.1,83,,82.3,90,,81.8,88,,72.8,79,,74.7,79,,69.6,75,,, , , , , 

N,412,,77.6,83,,82.5,90,,81.7,88,,72.6,78,,74.3,78,,68.9,75,,, , , , , 
E,118,,80.6,89,,83.5,90.5,,83.6,91,,74.9,82.5,,76.8,82,,71.5,79.5,,, , , , , 
S,11,,70.8,79,,68.8,68,,67,72,,68.4,70,,68.5,76,,74.6,79,,, , , , , 
W,8,,72.8,82,,76.9,87,,78.4,85,,59.9,61,,72.9,77.5,,72,82,,, , , , , 

NE,530,,78.3,83,,82.7,90,,82.2,88.5,,73.1,79,,74.8,80,,69.5,75,,, , , , , 
EW,126,,80.1,89,,83.1,90,,83.3,91,,73.9,81.5,,76.5,82,,71.5,80,,, , , , , 
SW,19,,71.6,79,,72.2,77,,71.8,77,,64.8,66,,70.4,77,,73.5,81,,, , , , , 
WEN,538,,78.2,83,,82.6,90,,82.1,88.5,,72.9,79,,74.8,79.5,,69.5,75,,, , , , , 
EWS,137,,79.3,87,,82,90,,82,88,,73.5,81,,75.9,82,,71.8,80,,, , , , , 
'''
def MakeCvsSpreadsheet(test_year, campuses, avg, med, numSummedStudents, outpath, outfile):

    try:
        os.makedirs(outpath)
    except:
        pass   # os.mkdirs throws if dir already exists! :(
    #

    filepath = os.path.join(outpath, outfile)
    f = open(filepath, 'w')

    f.write('ICHE Test Results ' + str(test_year) + ',,,,,,,,,,,,,,,,,,\n')
    f.write('\n')
    f.write(',,,Composite,,,Vocabulary,,,Reading,,,Language,,,Mathematics,,,Sources\n')
    f.write('Grade,#Stu,,Avg.,Med.,,Avg.,Med.,,Avg.,Med.,,Avg.,Med.,,Avg.,Med.,,Avg.,Med.\n')

    for campus in campuses:
        if campus == 'nesw':
            out_campus = 'ALL'
        else:
            out_campus = campus.upper()
        #

        f.write('%s,%d,,%.1f,%.1f,,%.1f,%.1f,,%.1f,%.1f,,%.1f,%.1f,,%.1f,%.1f,,%.1f,%.1f\n' % (
            out_campus, eval("numSummedStudents['" + campus + "']"),
            eval("avg['" + campus + "']['composite']"),   eval("med['" + campus + "']['composite']"),
            eval("avg['" + campus + "']['vocabulary']"),  eval("med['" + campus + "']['vocabulary']"),
            eval("avg['" + campus + "']['reading']"),     eval("med['" + campus + "']['reading']"),
            eval("avg['" + campus + "']['language']"),    eval("med['" + campus + "']['language']"),
            eval("avg['" + campus + "']['mathematics']"),  eval("med['" + campus + "']['mathematics']"),
            eval("avg['" + campus + "']['sources']"),     eval("med['" + campus + "']['sources']")
        ) )
        ''' This and above make binary equal files -- just checking :)
        f.write('%s,%d,,%s,%s,,%s,%s,,%s,%s,,%s,%s,,%s,%s,,%s,%s\n' % (
            out_campus, eval("numSummedStudents['" + campus + "']"),
            RoundStr( eval("avg['" + campus + "']['composite']") ),   RoundStr( eval("med['" + campus + "']['composite']") ),
            RoundStr( eval("avg['" + campus + "']['vocabulary']") ),  RoundStr( eval("med['" + campus + "']['vocabulary']") ),
            RoundStr( eval("avg['" + campus + "']['reading']") ),     RoundStr( eval("med['" + campus + "']['reading']") ),
            RoundStr( eval("avg['" + campus + "']['language']") ),    RoundStr( eval("med['" + campus + "']['language']") ),
            RoundStr( eval("avg['" + campus + "']['mathematics']") ), RoundStr( eval("med['" + campus + "']['mathematics']") ),
            RoundStr( eval("avg['" + campus + "']['sources']") ),     RoundStr( eval("med['" + campus + "']['sources']") )
        ) )
        '''
        if out_campus == 'ALL' or out_campus == 'W':
            f.write('\n')
        #
    #

    f.close()
    print "Generated CSV Spreadsheet"

#  MakeCvsSpreadsheet()


'''
def RoundStr(inVal):
    v = str(int( round(inVal, 1) * 10))
    v2 = v[:-1] + '.' + v[-1]
    return v2
#
'''


def MakePdfTable(campuses, avg, med, numSummedStudents, test_year, outpath, outfile):
    '''
    Generates a PDF table and saves it in the specified file.

       Coordinate system:

             | page
           ---+-----
              |
    '''
    try:
        os.makedirs(outpath)
    except:
        pass   # os.mkdirs throws if dir already exists! :(
    #

    filepath = os.path.join(outpath, outfile)

    # Make an A4-size canvas.
    #pagesize = (max(A4), min(A4))   # Landscape
    pagesize = (min(A4), max(A4))   # Portrait
    c = canvas.Canvas(filepath, pagesize)

    # Make a border
    width, height = pagesize
    #print 'width, height =', width, height
    c.setLineWidth(1)
    #c.rect(36, 36, width-72, height-72, stroke=1, fill=0)   # x, y, width, height, stroke, fill   -- 1/2 inch margins
    c.rect(18, 18, width-36, height-36, stroke=1, fill=0)   # x, y, width, height, stroke, fill   -- 1/4 inch margins

    # Title
    c.setFont("Times-Roman", 24)
    c.drawCentredString( width / 2, height * .87, 'ICHE Test Results ' + test_year)

    # Table grids
    c.setStrokeColor('black')
    c.setFillColor('black')
    c.setLineCap(0)
    c.setLineJoin(1)

    numGrids =  2
    numCols  =  8
    numRows  = 11

    left     = 0.75 * inch
    cell_w   = 0.85 * inch
    cell_h   = 0.22 * inch

    legend_top = 9 * inch

    for gridNum in range(numGrids):

        # Table Labels
        c.setFont("Times-Bold", 12)
        if gridNum == 0:
            c.drawString( left - 0.2 * inch, legend_top + cell_h, 'Averages')
        else:
            c.drawString( left - 0.2 * inch, legend_top + cell_h, 'Medians')
        #

        # Verticals
        c.setLineWidth(1)
        for col in range(numCols + 1):
            c.line(left + cell_w * col, legend_top, left + cell_w * col, legend_top - cell_h * numRows)
        #

        # Horizontals
        for row in range(numRows + 1):
            if row < 2:
                c.setLineWidth(2)
            else:
                c.setLineWidth(1)
            #
            c.line(left, legend_top - cell_h * row, left + cell_w * numCols, legend_top - cell_h * row)
        #

        legend_top = 5.5 * inch
    #

    # Headings
    c.setFont("Times-Bold", 10)
    c.setFillColor('black')

    legend_list = ['Grade', '#Students', 'Composite', 'Vocabulary', 'Reading', 'Language', 'Mathematics', 'Sources']

    legend_top = 9 * inch

    for gridNum in range(numGrids):
        for col in range(len(legend_list)):
            c.drawCentredString(left + col * cell_w + cell_w/2, legend_top - cell_h + 0.055 * inch, legend_list[col])
        #

        legend_top = 5.5 * inch
    #

    # Table data
    c.setFont("Times-Roman", 10)
    legend_top = 9 * inch

    for gridNum in range(numGrids):
        y = legend_top - cell_h - cell_h + 0.055 * inch

        for campus in campuses:
            if campus == 'nesw':
                cu = 'All'
            else:
                cu = campus.upper()
            #

            x = left + cell_w/2

            for i, legend in enumerate(legend_list):
                if i == 0:
                    c.drawRightString(x + 0.1 * inch, y, cu )

                elif i == 1:
                    c.drawRightString(x + 0.1 * inch, y, str(numSummedStudents[campus]) )

                else:
                    if gridNum == 0:
                        c.drawCentredString(x, y, str( round(avg[campus][legend.lower()], 1) ) )
                    else:
                        c.drawCentredString(x, y, str( round(med[campus][legend.lower()], 1) ) )
                    #
                #
                x = x + cell_w
            #

            y = y - cell_h
        #

        legend_top = 5.5 * inch
    #

    # Notes
    y = 2 * inch
    note_1 = 'NOTES:'
    note_2 = 'Scores shown are taken from both ITBS and ITED tests.'
    note_3 = "ITBS 'language total' is combined with ITED 'revising written material'."
    note_4 = "ITBS 'sources total' is combined with ITED 'sources of information'."
    c.drawString(left - 0.2 * inch, y - (2 * 0.18 * inch), note_1)
    c.drawString(left,              y - (3 * 0.18 * inch), note_2)
    c.drawString(left,              y - (4 * 0.18 * inch), note_3)
    c.drawString(left,              y - (5 * 0.18 * inch), note_4)

    # Generate PDF and save file
    c.showPage()
    c.save()

    print "Generated PDF Table"

# End MakePdfTable()


#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    '''
    Program starts here.
    '''
    print 'Student_Norms v' + version.version

    test_year = sys.argv[1]
    print 'test year is: ' + test_year

    # Campuses and campus combinations to compute averages and medians for.
    #campuses = ['nesw', 'n', 'e', 's', 'w', 'ne', 'ew', 'sw', 'new', 'esw']
    # Grades
    grades = ['3','4','5','6','7','8','9','10','11','12']

    averages, medians, numSummedStudents = GetDbScores(grades, test_year)

    print averages
    print medians
    print numSummedStudents


    outpath = './output/'
    pdf_outfile = 'ICHE_Test_Results_Norms_' + test_year + '.pdf'
    MakePdfTable(grades, averages, medians, numSummedStudents, test_year, outpath, pdf_outfile)

    # Display the newly-generated .cvs!
    #os.chdir(outpath)

# End main


# EOF

