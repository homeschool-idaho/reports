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
   cursor.execute( "".join(['SELECT DISTINCT score_student_data.region_num, '
                            'score_student_data.f_name, score_student_data.l_name, '
                            'testing_history.summa, testing_history.whos_who, score_student_data.grade, '
                            'member.street, member.city, member.state, member.zip, member.phone_home, '
                            'score_npr.composite, student.student_id '
                            'FROM '
                            '    score_student_data, testing_history, member, student, score_npr '
                            'WHERE '
                            '    score_student_data.student_id = student.student_id '
                            'AND score_student_data.score_id   = score_npr.score_id '
                            'AND student.member_id             = member.member_id '
                            'AND student.student_id            = testing_history.student_id '
                            'AND testing_history.grade >= "5" '
                            'AND testing_history.test_year = "' + str(test_year) + '" '  	                         
                            'AND year( score_student_data.date_tested ) = "' + str(test_year) + '" '
                            'AND score_npr.composite >= "80" '
                            'LIMIT 3000 ' ] ) )

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


def GetCompositeScoreForStudent(cursor, student_id, year, score ):
   cursor.execute( "".join(['SELECT DISTINCT score_student_data.region_num, '
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
                            'AND testing_history.grade >= "5" '
                            'AND testing_history.test_year = "' + str(year) + '" '  	                         
                            'AND year( score_student_data.date_tested ) = "' + str(year) + '" '
                            'AND score_npr.composite >= "' + str(score) + '" '
                            'AND student.student_id = "' + str(student_id) + '"'
                            'LIMIT 3000 ' ] ) )

   student_data = list( cursor.fetchall() )
   print student_data
   
   try:
      composite = student_data[0][11]
   except:
      composite = ''
      
   return composite

#  GetCompositeScoreForStudent()


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

   f.write("ICHE Summa / Who's Who Report " + str(test_year) + ' -- Grades 9-12,,,,,,,\n')
   f.write('\n')
   f.write(', , , SUMA, , , , WHO\'S WHO, , , , , , , ,\n')
   f.write('Region, Student Name, %s, %s, %s, %s, %s, %s, %s, %s, Grade, Street, City, State, Zip, Phone\n' %\
           (test_year_m3, test_year_m2, test_year_m1, test_year_m0,
            test_year_m3, test_year_m2, test_year_m1, test_year_m0) )


   db = MySQLdb.connect( host = "net.iche-idaho.org", user = "iche", 
                        passwd = "s1lvercreek", db = "icherstest")
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
         
         line = '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n' % \
              (student[0], student[1] + ' ' + student[2], s_m3, s_m2, s_m1, s_m0,
               w_m3, w_m2, w_m1, w_m0, student[5], street, student[7],
               student[8], student[9], phone)

         f.write(line)
         ct = ct + 1			
      #
   #

   f.write('\n')
   f.write('%s Students' % ct)
   f.close()

   print "Generated CSV 9-12 Sunmma Who Spreadsheet"

#  MakeCvs_9_12_Summa_Who_Spreadsheet()


"""
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

	legend_list = ['Campus', '#Students', 'Composite', 'Vocabulary', 'Reading', 'Language', 'Sources', 'Mathematics']

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
"""

#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   '''
	Program starts here. Expects the test year as the only argument.
	'''
   print 'make_whos_who_reports v' + version.version

   test_year = sys.argv[1]

   data = GetDbScores(test_year)

   outpath = '.\\output'

   csv_outfile = 'ICHE_5_8_Whos_Who_Report_' + test_year + '.csv'
   MakeCvs_5_8_Who_Spreadsheet(data, test_year, outpath, csv_outfile)

   csv_outfile = 'ICHE_9_12_Whos_Who_Report_' + test_year + '.csv'
   MakeCvs_9_12_Who_Spreadsheet(data, test_year, outpath, csv_outfile)

   csv_outfile = 'ICHE_9_12_Summa_Who_Report_' + test_year + '.csv'
   MakeCvs_9_12_Summa_Who_Spreadsheet(data, test_year, outpath, csv_outfile)

   #pdf_outfile = 'ICHE_Test_Results_' + test_year + '.pdf'
   #MakePdfTable(campuses, averages, medians, numSummedStudents, test_year, outpath, pdf_outfile)

   # Display the newly-generated .cvs!
   os.chdir(outpath)
   os.system(csv_outfile)

   #os.system(pdf_outfile)

# End main


# EOF

