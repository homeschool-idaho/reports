#-------------------------------------------------------------------------------
#
# make_histo_test1.py
#
#-------------------------------------------------------------------------------

# Python imports
from types import *
import os
import sys

# Third party imports
import MySQLdb
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, A3, A2, A1, A0, portrait, landscape
from reportlab.lib.units import inch


#-------------------------------------------------------------------------------
# Utility Functions
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------
# Member table
#-------------------------------------------------------------------------------

def GetMemberTable():
	cursor.execute("SELECT * from member limit 0, 6000")
	return cursor.fetchall()
#


#-------------------------------------------------------------------------------
# Connect 
#-------------------------------------------------------------------------------

db = MySQLdb.connect( host = "net.iche-idaho.org", user = "sugarloaf6160", 
							 passwd = "goldm1ning4fun", db = "ichetemp")
cursor = db.cursor()




def Legend(c, x, y, color, desc, fontSize):
	'''
	Draws a colored box and descriptive text at the given location.
	'''
	c.setStrokeColorRGB(0,0,0)
	if type(color) == TupleType:
		c.setFillColorRGB(1,0,1)
	else:
		c.setFillColor(color)
	#
	c.setLineWidth(1)
	height = fontSize * 0.7
	width  = height * 1.618   # The Golden Ratio
	c.rect(x - fontSize/10, y, width, height, stroke=1, fill=1)   #x, y, width, height, stroke=1, fill=0
	
	c.setFont("Times-Roman", fontSize)
	c.setFillColorRGB(0,0,0)
	horizSpacer = width + height
	c.drawString( x + horizSpacer, y, desc)
#


def MakePdfChart(datafile, outfile):
	
	# Make a canvas
	pagesize = (max(A1), min(A1))
	c = canvas.Canvas(filename, pagesize)

	# Make a border at 1/2 inch margins
	width, height = pagesize
	c.setLineWidth(3)
	c.rect(36, 36, width-72, height-72, stroke=1, fill=0)   # x, y, width, height, stroke, fill

	# Title
	c.setFont("Times-Roman", 40)   #Helvetica", 36)
	c.drawCentredString( width/2, height*.950, 'SCHOOL DISTRICT COMPARISON')
	c.setFont("Times-Roman", 26)
	c.drawCentredString( width/2, height*.920, 'Comparison of Idaho Coalition of Home Educators,')
	c.drawCentredString( width/2, height*.900, 'State of Idaho School Districts, and National School Districts')
	c.drawCentredString( width/2, height*.880, 'Iowa Tests of Basic Skills & Iowa Tests of Educational Development')
	c.drawCentredString( width/2, height*.860, '- 2008 -')
	
	# Legends
	iche     = 'ICHE:  Percentile ratings of home-educated students tested by Idaho Coalition of Home Educators treated as a single district on 2008 ITBS/ITED.'
	idaho    = 'IDAHO:  Statewide percentile ratings of Idaho public school students treated as a single district on 2001 ITBS/TAP (latest scores available).'
	national = 'NATIONAL:  Nationwide percentile ratings of public school districts.'
	Legend(c, 100, 160, (1,0,1), iche, 24)
	Legend(c, 100, 130, 'blue', idaho, 24)
	Legend(c, 100, 100, 'lightblue', national, 24)
	
	# Comments
	c.drawString(100, 220, 'Percentile ratings based on overall ITBS/ITED performance of students on a district-by-district '+\
					'basis with Idaho Coalition of Home Educators students and Idaho public school districts treated as single districts.')
	
	# Bar chart
	c.setLineWidth(3)
	rwidth  = width  * 0.8
	rheight = height * 0.6
	x = width  * 0.1
	y = height * 0.2
	c.rect(x, y, rwidth, rheight, stroke=1, fill=0)   # x, y, width, height, stroke, fill
	
	data = \
	[
		(99, 99, 97, 95, 87, 93),
		(56, 48, 59, 50, 56, 52),
		(50, 50, 50, 50, 50, 50),
		('Composite','Vocabulary','Reading','Language','Mathematics','Sources')
	]
	colors = ['magenta', 'blue', 'lightblue']
	
	c.setStrokeColorRGB(0,0,0)
	
	yAxisLabelStep = 10
	yAxisStep = rheight / 6
	yAxisFloor = 40
	
	c.setLineWidth(1)
	for i in range(6):
		c.drawString(x - width * 0.02, (y + (yAxisStep * i)) - (height * 0.004), str(yAxisFloor + (yAxisLabelStep * i)))
		c.line(x - width * 0.005, y + (yAxisStep * i), x + rwidth, y + (yAxisStep * i))
	#
	
	barWidth = width * 0.02
	clusterSpacing = barWidth * 1.5
	
	numClusters = len(data[0])
	barsPerCluster = len(data) - 1
	chartWidth = numClusters * ((barsPerCluster * barWidth) + clusterSpacing) - clusterSpacing
	barX = (width - chartWidth) / 2
	
	c.setLineWidth(1)
	for clusterNum in range( len(data[0]) ):
		#print 'clusterNum', clusterNum
		
		for barNum in range( len(data) ):
			#print 'barNum', barNum
			
			if barNum < 3:
				color = colors[barNum]
				c.setFillColor(color)
				
				value = data[barNum][clusterNum]
				barHeight =  value - yAxisFloor
				
				# Normalize the bar height to the chart height
				barHeight = (barHeight * rheight) / (100 - yAxisFloor)
				
				# Draw the bar
				c.rect(barX, y, barWidth, barHeight, stroke=1, fill=1)   # x, y, width, height, stroke, fill
				
				# Draw the var value square
				c.setFillColor('white')
				c.rect(barX + (barWidth * 0.1), y + barHeight - (barWidth * .9),
						 barWidth * 0.8, barWidth * 0.8, stroke=1, fill=1)   # x, y, width, height, stroke, fill
				
				# Draw the bar value
				c.setFillColor('black')
				valueXoffset = width  * 0.005
				valueYoffset = height * 0.020
				c.drawString(barX + valueXoffset, y + barHeight - valueYoffset, str(value))
				
				if barNum == 0:
					nameX = barX
				#
				
				barX += barWidth
			else:
				name = data[3][clusterNum]
				c.drawString(nameX, y - height * 0.02, name)
			#
		#
		barX += clusterSpacing
	#
	
	
	
	# Generate PDF and save file
	c.showPage()
	c.save()
	
# End MakeHistogram()


if __name__ == '__main__':
	'''
	Program starts here.
	'''
	datafile = sys.argv[1]
	outfile = datafile.replace('py', 'pdf')
	MakePdfChart(datafile, outfile)

	# Display the newly-generated charts!
	import os
	os.system(filename)
	
# End main





# EOF


