#-------------------------------------------------------------------------------
#
# pdf_processor.py
#
# processes the pdf profiles as received from Houghton Mifflin:
#
#   separates the class file(s) PDF's
#   into individual profiles (by student)
#
# Requires Python, MySqlDb.
# Requires pyPdf
#
# MAKE SURE THAT THE icherstest DB IS UP TO DATE!
#-------------------------------------------------------------------------------

# Python imports
from types import *
import os
import sys
import unicodedata

from pyPdf import PdfFileWriter, PdfFileReader
#import MySQLdb
#import orm

# def GetDbScores(test_year):
#     compositeSum = vocabularySum = readingSum = languageSum = mathematicsSum = sourcesSum = 0
#     studentNum = 0
#     numSummedStudents = 0
#
#     db = MySQLdb.connect(host="net.iche-idaho.org", user="iche",
#                          passwd="s1lvercreek", db="icherstest")
#     cursor = db.cursor()
#
#     cursor.execute("".join(['SELECT DISTINCT * '
#                             'FROM score_student_data '
#                             'WHERE (member_id is not null and year(date_tested) = "' + str(test_year) + '" ) '
#                             'order by year(date_tested), region_num, level '
#                             'LIMIT 0,3000']))
#
#     student_data = list(cursor.fetchall())  # From tuple
#
#     for student in student_data:
#         print student
#
#     print '########################'
#
#     #student_data.sort()  # Sorts by region, the first field
#
#     for student in student_data:
#         print student
#
#     print
#     print 'len(student_data)', len(student_data)
#
#     return student_data
#
# # End GetDbScores()

# def GetStudentCampus(type):
#     if type == "E":
#         return "EAST"
#     elif type == "W":
#         return "WEST"
#     elif type == "N":
#         return "NORTH"
#     elif type == "S":
#         return "SOUTH"


# def ProcessClassStudents(inputPath, outputPath, inputFilename, tested_students):
#
#     inputpdf = PdfFileReader(open(inputPath + inputFilename, "rb"))
#
#     for i in xrange(inputpdf.numPages):
#         output = PdfFileWriter()
#         output.addPage(inputpdf.getPage(i))
#         title = output.getDocumentInfo().title
#         outFilePath = outputPath + "" + tested_students[i].l_name + "_" + tested_students[i].f_name + ".pdf"
#         with open(outFilePath, "wb") as outputStream:
#             output.write(outputStream)
#
# # End ProcessClassStudents

def ProcessClassFile(inputPath, classInfo, outputPath):
    try:
        inputpdf = PdfFileReader(open(inputPath, "rb"))

        for i in xrange(inputpdf.numPages):
            output = PdfFileWriter()
            output.addPage(inputpdf.getPage(i))
            pdfText = inputpdf.getPage(i).extractText().encode('utf-8')
            index1 = pdfText.index("PERFORMANCE PROFILE FOR ") + len("PERFORMANCE PROFILE FOR ")
            index2 = pdfText.index("Iowa Assessments")
            filename = pdfText[index1:index2]
            outFilePath = outputPath + filename.replace(" ", "_") + ".pdf"
            with open(outFilePath, "wb") as outputStream:
                output.write(outputStream)
    except:
        print 'Error: ' + inputPath
    #


# End ProcessClassStudents

def ProcessPdfDirectory(inputPath, outputPath):

    # traverse root directory, and list directories as dirs and files as files
    for root, dirs, files in os.walk("."):
        path = root.split(os.sep)
        print((len(path) - 1) * '---', os.path.basename(root))
        for file in files:
            print(len(path) * '---', file)
            if len(path) > 2 and file <> "index.pdf" and file <> "openmefirst.pdf":
                ProcessClassFile(root + "/" + file, path[2], outputPath)

# End ProcessPdfDirectory

# def ProcessPdfDirectory(inputPath, outputPath, tested_students):
#
#     #loop through the students and save the individual profiles from each class
#     current_class = []
#     current_class_type = ""
#     current_class_grade = ""
#     for student in tested_students:
#         if (current_class_type <> "" and student.campus <> current_class_type) || (current_class_grade <> "" and student.grade <> current_class_grade):
#             inputFileName = student.grade + '_' + GetStudentCampus(student.campus) + '_CLASS_Individual Performance Profile.pdf'
#             ProcessClassStudents(inputPath, outputPath, inputFileName, current_class)
#             # current class is processed, now create the next class
#             current_class =[]
#             current_class_type = student.campus
#             current_class_grade = student.grade
#         else:
#             current_class_type = student.campus
#             current_class_grade = student.grade
#
#         # add the student to the class
#         current_class += student
#
# # End ProcessPdfDirectory()

#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    '''
    Program starts here.
    '''
    print 'pdfprocessor v0.1'

    test_year = sys.argv[1]
    print 'test year is: ' + test_year
    #tested_students = GetDbScores(test_year)
    inputPath = './profiles/'
    outpath = './output/'

    if os.path.isdir(outpath) == False:
        os.mkdir(outpath)
    #ProcessPdfDirectory(inputPath, outpath, tested_students)
    ProcessPdfDirectory(inputPath, outpath)

# End main


# EOF