# -------------------------------------------------------------------------------
#
# make_pdf_chart.py
#
# Requires Python, ReportLab, MySqlDb, and a PDF viewer such as Acrobat.
#
# -------------------------------------------------------------------------------

# Python imports
from types import *
import os
import sys
import imp

# Third party imports
import MySQLdb
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import HexColor, toColor
from reportlab.lib.pagesizes import A1
from reportlab.lib.units import inch

# ICHE imports
import orm
from pantone import *

# these need to be defined here (globally)
legend1_color = '#6989ff'
legend2_color = '#555555'  # This is the grayscale version
legend3_color = '#999999'  # This is the grayscale version


def __import__(name, globals=None, locals=None, fromlist=None):
    # Fast path: see if the module has already been imported.
    try:
        return sys.modules[name]
    except KeyError:
        pass

    # If any of the following calls raises an exception,
    # there's a problem we can't handle -- let the caller handle it.

    fp, pathname, description = imp.find_module(name)

    try:
        return imp.load_module(name, fp, pathname, description)
    finally:
        # Since we may exit via an exception, close fp explicitly.
        if fp:
            fp.close()
    #


#

# End __import__()

def GetDbScores(score_type, test_year):
    if not score_type in ['ICHE_2yr', 'ICHE_1yr']:
        print ('If pulling scores from the ICHE database, you must use one of "ICHE_2yr", "ICHE_1yr".')
        print ('These ase case-sensitive')
        sys.exit(1);
    #

    compositeSum = vocabularySum = readingSum = languageSum = mathematicsSum = sourcesSum = 0
    studentNum = 0
    numSummedStudents = 0

    # db = MySQLdb.connect( host = "net.iche-idaho.org", user = "sugarloaf6160",
    #							 passwd = "goldm1ning4fun", db = "ichetemp")
    db = MySQLdb.connect(host="net.iche-idaho.org", user="iche",
                         passwd="s1lvercreek", db="icherstest")
    cursor = db.cursor()

    cursor.execute("SELECT * from score_student_data limit 0, 6000")
    student_data = cursor.fetchall()

    if score_type == 'ICHE_2yr':
        where_years = '> 1'
    else:
        where_years = '= 1'
    #

    numTotalStudents = len(student_data)

    for row in student_data:
        student = orm.score_student_data(row)

        query_str = "SELECT * from testing_history where test_year = " + str(test_year) + \
                    " and testing_history_id = " + str(student.testing_history_id) + \
                    " and years_hs " + where_years + " limit 0, 6000"
        cursor.execute(query_str)
        testhist_data = cursor.fetchall()

        if len(testhist_data) == 0:
            print 'ERROR: Failed to get testing history for', student.f_name, student.l_name
            studentNum += 1
            continue
        #

        th = orm.testing_history(testhist_data[0])

        if (th.years_hs > 1 and score_type == 'ICHE_1yr') \
                or (th.years_hs == 1 and score_type == 'ICHE_2yr'):
            print "Skipping student", studentNum, "of", numTotalStudents, "due to number of home-school years (", th.years_hs, ") not as requested"
            studentNum += 1
            continue
        #

        cursor.execute("SELECT * from score_npr where score_id = " + str(student.score_id) + " limit 0, 6000")
        score_npr_data = cursor.fetchall()

        compositeSum += score_npr_data[0][24]
        vocabularySum += score_npr_data[0][1]
        readingSum += score_npr_data[0][3]
        languageSum += score_npr_data[0][10]
        mathematicsSum += score_npr_data[0][15]
        sourcesSum += score_npr_data[0][22]

        studentNum += 1
        numSummedStudents += 1
        print score_type, "; Processed student", studentNum, "of", numTotalStudents
    #

    compositeAvg = compositeSum / numSummedStudents
    vocabularyAvg = vocabularySum / numSummedStudents
    readingAvg = readingSum / numSummedStudents
    languageAvg = languageSum / numSummedStudents
    mathematicsAvg = mathematicsSum / numSummedStudents
    sourcesAvg = sourcesSum / numSummedStudents

    return [compositeAvg, vocabularyAvg, readingAvg, languageAvg, mathematicsAvg,
            sourcesAvg], numTotalStudents, numSummedStudents


# End GetDbScores()

def SetChartFillColor(c, color):
    if type(color) in [TupleType, ListType]:
        bHundredMax = False
        for n in color:
            if n > 1:
                bHundredMax = True
                break
        #
        #
        if bHundredMax:
            adjColors = []
            for n in color:
                newColor = n / 100.0
                adjColors.append(newColor)
            #
            usedColors = adjColors
        else:
            usedColors = color
    #
    else:
        if type(color) == StringType:
            lcColor = color.lower()  # string.lower(arg)
            if lcColor[0:3] == 'pms':
                pmsColor = int(lcColor[3:])
                cmykColors = pantoneColors[pmsColor]

                adjColors = []
                for n in cmykColors:
                    newColor = n / 100.0
                    adjColors.append(newColor)
                #
                usedColors = adjColors

            elif lcColor[0] == 'p':
                pmsColor = int(lcColor[1:])
                cmykColors = pantoneColors[pmsColor]

                adjColors = []
                for n in cmykColors:
                    newColor = n / 100.0
                    adjColors.append(newColor)
                #
                usedColors = adjColors
            else:
                usedColors = color
        #
        else:
            usedColors = color
    #
    #

    c.setFillColor(toColor(usedColors))


# End SetChartFillColor()


def Legend(c, x, y, color, desc, fontSize):
    '''
    Draws a colored box and descriptive text at the given location.
    '''
    c.setStrokeColor('black')  # Outline Color

    SetChartFillColor(c, color)
    # c.setFillColor( toColor(color) )

    c.setLineWidth(1)
    height = fontSize * 0.7
    width = height * 1.618  # The Golden Ratio
    c.rect(x - fontSize / 10, y, width, height, stroke=1, fill=1)  # x, y, width, height, stroke=1, fill=0

    c.setFont("Times-Roman", fontSize)
    c.setFillColor('black')  # Text color
    horizSpacer = width + height
    c.drawString(x + horizSpacer, y, desc)


# End Legend()


def MakePdfChart(datafile, outfile):
    '''
    Reads the user-named data file and potentially the ICHE database.
    Generates a PDF chart and saves it in the specified file.
    '''

    # Make an A1-size canvas. It scales down properly when printing on smaller paper.
    pagesize = (max(A1), min(A1))
    c = canvas.Canvas(outfile, pagesize)

    # Make a border at 1/2 inch margins
    width, height = pagesize
    c.setLineWidth(3)
    c.rect(36, 36, width - 72, height - 72, stroke=1, fill=0)  # x, y, width, height, stroke, fill

    # Import the data file
    data = __import__(datafile.split('.')[0])
    if data.chart_3D:
        bFlatChart = False
    else:
        bFlatChart = True
    #

    # Title
    c.setFont("Times-Roman", 48)  # 48
    c.drawCentredString(width / 2, height * .950, data.title)

    c.setFont("Times-Roman", 28)  # 28, 30, 32
    c.drawCentredString(width / 2, height * .920, data.subtitle1)
    c.drawCentredString(width / 2, height * .900, data.subtitle2)
    if len(data.subtitle4.strip()) == 0:
        c.setFont("Times-Roman", 32)  # 32, 34, 36
        c.drawCentredString(width / 2, height * .880, data.subtitle3)
    else:
        c.drawCentredString(width / 2, height * .880, data.subtitle3)
        c.setFont("Times-Roman", 32)  # 32, 34, 36
        c.drawCentredString(width / 2, height * .860, data.subtitle4)
    #

    # Comments
    c.setFont("Times-Roman", 28)  # 28, 30, 32
    c.drawString(300, 240, data.comment1)
    c.drawString(300, 215, data.comment2)

    # Legends
    Legend(c, 300, 160, legend1_color, data.legend1_text, 28)  # 28, 30, 32
    Legend(c, 300, 130, legend2_color, data.legend2_text, 28)
    Legend(c, 300, 100, legend3_color, data.legend3_text, 28)

    # Bar chart
    c.setLineWidth(3)
    rwidth = width * 0.8
    rheight = height * 0.6
    x = width * 0.1
    y = height * 0.21

    barWidth = width * 0.025
    if not bFlatChart:
        x += barWidth / 2
    #

    c.setLineCap(1)
    c.setLineJoin(1)
    c.setStrokeColor('black')

    if bFlatChart:
        c.rect((width - rwidth) / 2, y, rwidth, rheight, stroke=1, fill=0)  # x, y, width, height, stroke, fill
    else:
        c.rect(((width - rwidth) / 2) + barWidth / 2, y, rwidth, rheight, stroke=1,
               fill=0)  # x, y, width, height, stroke, fill
    #

    if bFlatChart:
        pass
    else:
        c.setFillColor('lightgrey')
        rtSide = x + rwidth

        c.setLineCap(1)
        c.setLineJoin(1)
        c.setStrokeColor('black')
        # Bottom
        p = c.beginPath()
        p.moveTo(rtSide, y)
        p.lineTo(rtSide - barWidth / 3, y - barWidth / 3)
        p.lineTo(x - barWidth / 3, y - barWidth / 3)
        p.lineTo(x, y)
        p.lineTo(rtSide, y)
        c.drawPath(p, fill=1)

        # Left
        p = c.beginPath()
        p.moveTo(x, y)
        p.lineTo(x, y + rheight)
        p.lineTo(x - barWidth / 3, y + rheight - barWidth / 3)
        p.lineTo(x - barWidth / 3, y - barWidth / 3)
        p.lineTo(x, y)
        c.drawPath(p, fill=1)
    #

    chart_data = \
        [
            (50, 50, 50, 50, 50),
            (50, 50, 50, 50, 50),
            (50, 50, 50, 50, 50),
            ('Composite', 'Vocabulary', 'Reading', 'Language', 'Mathematics')
        ]
    colors = [legend1_color, legend2_color, legend3_color]

    # Potentially get data from the ICHE database
    if type(data.scores1) == StringType:
        scores_list, numTotalStudents1, numSummedStudents1 = GetDbScores(data.scores1, data.test_year)
        chart_data[0] = scores_list
    else:
        chart_data[0] = data.scores1
    #

    if type(data.scores2) == StringType:
        scores_list, numTotalStudents2, numSummedStudents2 = GetDbScores(data.scores2, data.test_year)
        chart_data[1] = scores_list
    else:
        chart_data[1] = data.scores2
    #

    if type(data.scores3) == StringType:
        scores_list, numTotalStudents3, numSummedStudents3 = GetDbScores(data.scores3, data.test_year)
        chart_data[2] = scores_list
    else:
        chart_data[2] = data.scores3
    #

    c.setStrokeColor('black')  # Line color
    c.setFillColor('black')  # Text color
    c.setLineCap(1)
    c.setLineJoin(1)

    yAxisTop = 90
    yAxisSections = 5
    yAxisLabelStep = 10
    yAxisStep = rheight / yAxisSections
    yAxisFloor = 40

    # Y Axis labels and horizontal mid-chart lines
    c.setLineWidth(1)
    if bFlatChart:
        yAxisLabelXoffset = 0.02
        yAxisLabelYoffset = 0
    else:
        yAxisLabelXoffset = 0.025
        yAxisLabelYoffset = barWidth / 3
    #
    # adjust here for top of axis, this will determine # of sections from the yAxisFloor (40)
    # for 6 sections 40 - 100, height should be 0.004
    # for 5 sections 40 - 90, height should be
    for i in range(yAxisSections):
        c.drawString(x - width * yAxisLabelXoffset,
                     (y + (yAxisStep * i)) - (height * 0.004) - yAxisLabelYoffset,
                     str(yAxisFloor + (yAxisLabelStep * i)))

        c.line(x, y + (yAxisStep * i), x + rwidth, y + (yAxisStep * i))

        if not bFlatChart:
            c.line(x - barWidth / 3, y + (yAxisStep * i) - barWidth / 3, x, y + (yAxisStep * i))
    #
    #

    if bFlatChart:
        clusterSpacing = barWidth * 1.5
    else:
        clusterSpacing = barWidth * 2
    #

    numClusters = len(chart_data[0])
    barsPerCluster = len(chart_data) - 1
    chartWidth = numClusters * ((barsPerCluster * barWidth) + clusterSpacing) - clusterSpacing
    if bFlatChart:
        barX = (width - chartWidth) / 2
    else:
        barX = ((width - chartWidth) / 2) + barWidth / 2
    #

    c.setLineWidth(1)
    for clusterNum in range(len(chart_data[0])):
        # print 'clusterNum', clusterNum

        for barNum in range(len(chart_data)):
            # print 'barNum', barNum

            if barNum < 3:
                color = colors[barNum]
                SetChartFillColor(c, color)

                value = chart_data[barNum][clusterNum]
                barHeight = value - yAxisFloor

                # Normalize the bar height to the chart height
                barHeight = (barHeight * rheight) / (yAxisTop - yAxisFloor)

                # Draw the bar
                if bFlatChart:
                    # Flat Bar
                    c.rect(barX, y, barWidth, barHeight, stroke=1, fill=1)  # x, y, width, height, stroke, fill

                else:
                    # 3D Bar
                    SetChartFillColor(c, color)
                    c.setStrokeColor('black')
                    c.setLineWidth(1)
                    c.setLineCap(1)
                    c.setLineJoin(1)

                    #   Front
                    c.rect(barX - barWidth / 3, y - barWidth / 3, barWidth, barHeight, stroke=1, fill=1)

                    #   Top
                    p = c.beginPath()
                    p.moveTo(barX, y + barHeight)
                    p.lineTo(barX + barWidth, y + barHeight)
                    p.lineTo(barX + barWidth - barWidth / 3, y + barHeight - barWidth / 3)
                    p.lineTo(barX - barWidth / 3, y + barHeight - barWidth / 3)
                    p.lineTo(barX, y + barHeight)
                    c.drawPath(p, fill=1)

                    #   Right side
                    p = c.beginPath()
                    p.moveTo(barX + barWidth - barWidth / 3,
                             y - barWidth / 3)  # + barWidth/3 to override colored line immediately above
                    p.lineTo(barX + barWidth - barWidth / 3, y + barHeight - barWidth / 3)
                    p.lineTo(barX + barWidth, y + barHeight)
                    p.lineTo(barX + barWidth, y)
                    p.lineTo(barX + barWidth - barWidth / 3, y - barWidth / 3)
                    c.drawPath(p, fill=1)

                    # Adjust position for drawing value square below
                    barX = barX - barWidth / 3
                    barHeight = barHeight - barWidth / 3
                #

                # Draw the var value square
                c.setFillColor('white')
                c.rect(barX + (barWidth * 0.15), y + barHeight - (barWidth * .85),
                       barWidth * 0.7, barWidth * 0.7, stroke=1, fill=1)  # x, y, width, height, stroke, fill

                # Draw the bar value
                c.setFillColor('black')
                valueXoffset = width * 0.0058
                valueYoffset = height * 0.023
                c.drawString(barX + valueXoffset, y + barHeight - valueYoffset, str(value))

                if barNum == 0:
                    nameX = barX + barWidth / 2
                #

                if bFlatChart:
                    # Flat Bar
                    barX += barWidth
                else:
                    # 3D Bar
                    barX += (barWidth + barWidth / 3)
            #
            else:
                c.setFont("Times-Roman", 34)  # Font family, size

                name = chart_data[3][clusterNum]

                if bFlatChart:
                    c.drawString(nameX, y - height * 0.02, name)
                else:
                    c.drawString(nameX, y - barWidth / 3 - height * 0.02, name)
            #
        #
        #
        barX += clusterSpacing
    #

    # Generate PDF and save file
    c.showPage()
    c.save()

    print
    if type(data.scores1) == StringType:
        print 'There were', numSummedStudents1, 'of', numTotalStudents1, 'students for', data.scores1
    #

    if type(data.scores2) == StringType:
        print 'There were', numSummedStudents2, 'of', numTotalStudents2, 'students for', data.scores2
    #

    if type(data.scores3) == StringType:
        print 'There were', numSummedStudents3, 'of', numTotalStudents3, 'students for', data.scores3
    #

    print "Generated PDF chart"


# End MakePdfChart()


if __name__ == '__main__':
    # only takes one parameter (color or nothing for black and white (default))
    param1 = sys.argv[1]

    if param1 == 'color':
        color = True
    else:
        color = False

    outpath = './output/'

    datafile1 = 'sdc_config.py'

    if color == True:
        outfile = 'sdc_chart.pdf'
    else:
        outfile = 'sdc_chart_bw.pdf'

    path_outfile1 = os.path.join(outpath, outfile)

    datafile2 = 'trc_config.py'

    if color == True:
        outfile = 'trc_chart.pdf'
    else:
        outfile = 'trc_chart_bw.pdf'

    path_outfile2 = os.path.join(outpath, outfile)

    datafile3 = 'tra_config.py'

    if color == True:
        outfile = 'tra_chart.pdf'
    else:
        outfile = 'tra_chart_bw.pdf'

    path_outfile3 = os.path.join(outpath, outfile)

    # Set light and dark values. The third bar will be shaded 1/2 way in the middle.
    lightgray = 90  # Using percentage (0-100) method
    darkgray = 40
    if not color:
        medgray = darkgray + ((lightgray - darkgray) / 2)
        legend1_color = (medgray, medgray, medgray)
        legend2_color = (lightgray, lightgray, lightgray)
        legend3_color = (darkgray, darkgray, darkgray)
    else:
        legend1_color = '#6989ff'
        legend2_color = '#555555'  # This is the grayscale version
        legend3_color = '#999999'  # This is the grayscale version

    try:
        os.mkdir(outpath)
    except:
        pass

    MakePdfChart(datafile1, path_outfile1)
    MakePdfChart(datafile2, path_outfile2)
    MakePdfChart(datafile3, path_outfile3)

    # Display the newly-generated charts!
# os.chdir(outpath)
# os.system(outfile)

# End main


# EOF
