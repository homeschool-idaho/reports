#-------------------------------------------------------------------------------
#
# read_db_test1.py
#
#-------------------------------------------------------------------------------

'''
#-------------------------------------------------------------------------------
# Utility Functions
#-------------------------------------------------------------------------------
class Enum:

	def MakeEnums(self, prefix, colNamesCSV):
		colNames = colNamesCSV.split(',')
		for i in range( len(colNames) ):
			cmd = 'self.' + prefix + colNames[i] + '=' + str(i)
			exec cmd
		#
	#
#
e = Enum()


#-------------------------------------------------------------------------------
# Member table
#-------------------------------------------------------------------------------
e.MakeEnums( 'member_', 
'member_id,mother_f_name,mother_l_name,mother_m_init,father_f_name,father_l_name,father_m_init,'+\
'street,city,state,zip,phone_home,phone_work,region,email,num_students,num_idcards,date_entered,'+\
'date_modified,membership_expires,modified_by')

def GetMemberTable():
	cursor.execute("SELECT * from member limit 0, 6000")
	return cursor.fetchall()
#


#-------------------------------------------------------------------------------
# Connect 
#-------------------------------------------------------------------------------

import MySQLdb

db = MySQLdb.connect( host = "net.iche-idaho.org", user = "sugarloaf6160", 
							 passwd = "goldm1ning4fun", db = "ichetemp")
cursor = db.cursor()


#-------------------------------------
# Get Data
#-------------------------------------
memberTable = GetMemberTable()
print len(memberTable), 'members'

bins = [0] * 10
i = 0
for member in memberTable:
	#print member
	#print 'phone #:', member[e.member_phone_home]
	if len(member[e.member_phone_home]) != len('2083755775'):
		print i, member
		i += 1
	else:
		# Make a histogram of the phone numbers
		number = int(member[e.member_phone_home][3:])
		bin = number / 1000000
		bins[bin] += 1
	#
# End for
'''

#-------------------------------------
# Display Histogram with ReportLab
#-------------------------------------
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, A3, A2, A1
	
#def hello(c):
	#c.drawString(100,100, "HelloWorld!")
##   

#c = canvas.Canvas("hello.pdf")
#hello(c)
#c.showPage()
#c.save()

def MakeHistogram(filename): #, data):
	'''
	c = canvas.Canvas(filename, pagesize=A2)   # A2 = C size = 17x22 inches
	width, height = A2
	c.rect(36, 36, width-72, height-72, stroke=1, fill=0)   # x, y, width, height, stroke, fill
	'''
	
	'''
	#framePage(c, 'Color Demo - RGB Space - page %d' % c.getPageNumber())
	miny = 10000000
	maxy = 0
	
	for bin in bins:
		print bin
		if bin > maxy:
			maxy = bin
		if bin < min:
			miny = bin
	#

	minx = 0
	maxx = len(data)
	'''
	
	'''
	x = 10
	for bin in data:
		c.setFillColor(colors.red)
		c.rect(x, 100, 10, bin, stroke=1, fill=1)   # x, y, width, height, stroke, fill
		x += 20
		
		#all_colors = reportlab.lib.colors.getAllNamedColors().items()
		#all_colors.sort() # alpha order by name
		#c.setFont('Times-Roman', 12)
		#c.drawString(72,730, 'This shows all the named colors in the HTML standard.')
		#y = 700
		#for (name, color) in all_colors:
			#c.setFillColor(colors.black)
			#c.drawString(100, y, name)
			#c.setFillColor(color)
			#c.rect(200, y-10, 300, 30, fill=1)
			#y = y - 40
			#if y < 100:
				#c.showPage()
				#framePage(c, 'Color Demo - RGB Space - page %d' % c.getPageNumber())
				#y = 700
	#
	c.showPage()
	c.save()
	'''
	
	
	#------------------------------
	from reportlab.graphics.shapes import Drawing
	from reportlab.graphics.charts.barcharts import VerticalBarChart
	drawing = Drawing(1600, 1200)
	data = \
	[
		(99, 99, 97, 95, 87, 93),
		(56, 48, 59, 50, 56, 52),
		(50, 50, 50, 50, 50, 50)
	]
	bc = VerticalBarChart()
	bc.x = 250           # Position
	bc.y = 250
	bc.height = 700     # Size
	bc.width = 1000
	#bc.data = [data]    # Expects a list of tuples; one tuple for each series
	bc.data = data    # Expects a list of tuples; one tuple for each series
	bc.strokeColor = colors.black
	bc.valueAxis.valueMin = 0
	#top = (maxy + 100) / 100
	#top = top * 100
	#bc.valueAxis.valueMax = top
	#bc.valueAxis.valueStep = 100
	bc.groupSpacing = 100
	bc.barSpacing = 0
	bc.barWidth = 50
	bc.categoryAxis.labels.boxAnchor = 'ne'
	bc.categoryAxis.labels.dx = 8
	bc.categoryAxis.labels.dy = -2
	bc.categoryAxis.labels.angle = 0
	bc.categoryAxis.labels._value.fontSize = 20
	bc.categoryAxis.categoryNames = ['Composite','Vocabulary','Reading','Language','Mathematics','Sources']
	drawing.add(bc)
	
	from reportlab.graphics import renderPDF
	renderPDF.drawToFile(drawing, filename, 'Test')
	
	'''
	from reportlab.graphics.shapes import Drawing
	from reportlab.graphics.charts.barcharts import VerticalBarChart
	drawing = Drawing(400, 200)
	data = [
	(13, 5, 20, 22, 37, 45, 19, 4),
	(14, 6, 21, 23, 38, 46, 20, 5)
	]
	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black
	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 50
	bc.valueAxis.valueStep = 10
	bc.categoryAxis.labels.boxAnchor = 'ne'
	bc.categoryAxis.labels.dx = 8
	bc.categoryAxis.labels.dy = -2
	bc.categoryAxis.labels.angle = 30
	bc.categoryAxis.categoryNames = ['Jan-99','Feb-99','Mar-99','Apr-99','May-99','Jun-99','Jul-99','Aug-99']
	drawing.add(bc)
	
	from reportlab.graphics import renderPDF
	renderPDF.drawToFile(drawing, 'barchart.pdf', 'My First Bar Chart')
	'''
	
#  End MakeHistogram()

filename = 'histogram.pdf'
MakeHistogram(filename) #, bins)


# Display the newly-generated charts!
import os
os.system(filename)




'''
Unused

def framePage(canvas, title):
	canvas.setFont('Times-BoldItalic',20)
	
	canvas.drawString(inch, 10.5 * inch, title)

	canvas.setFont('Times-Roman',10)
	canvas.drawCentredString(4.135 * inch, 0.75 * inch, 'Page %d' % canvas.getPageNumber())

	#draw a border
	canvas.setStrokeColorRGB(1,0,0)
	canvas.setLineWidth(5)
	canvas.line(0.8 * inch, inch, 0.8 * inch, 10.75 * inch)
	#reset carefully afterwards
	canvas.setLineWidth(1)
	canvas.setStrokeColorRGB(0,0,0)
#


	def show_fonts(canvas):
		text = "Now is the time for all good men to..."
		x = 1.8*inch + 300
		y = 2.7*inch + 300
		for font in canvas.getAvailableFonts():
			canvas.setFont(font, 10)
			canvas.drawString(x, y, text)
			canvas.setFont("Helvetica", 10)
			canvas.drawRightString(x-10,y, font+":")
			y = y-13
		#
	#
	
	fonts = 0
	if fonts == 1:
		show_fonts(c)
	#
	
	sample_histogram = 0
	if sample_histogram == 1:
		miny = 10000000
		maxy = 0
	
		for bin in bins:
			print bin
			if bin > maxy:
				maxy = bin
			#
			if bin < min:
				miny = bin 
			#
		#
	
		minx = 0
		maxx = len(data)
	
		x = 100
		for bin in data:
			c.setFillColor(colors.red)
			c.rect(x, 100, 10, bin, stroke=1, fill=1)   # x, y, width, height, stroke, fill
			x += 20
		#
	#
'''



# EOF


