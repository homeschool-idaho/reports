#-------------------------------------------------------------------------------
# tra_config.py
#
# Test Results Analysis
#-------------------------------------------------------------------------------

title      = "TEST RESULTS ANALYSIS"

test_year  = 2019

subtitle1  = "Homeschool Idaho"
subtitle2  = "Iowa Tests of Basic Skills & Iowa Tests of Educational Development"
subtitle3  = "- " + str(test_year) + " -"
subtitle4  = ""


# The comment is placed under the chart and above the legend.
comment1   = ""
comment2   = ""

# Colors names you may use are most of the HTML color names. See
#    HTML Colors:    http://www.techiecoach.com/2007/05/03/html-color-names-table/
#    HTML Colors:    http://www.w3schools.com/htmL/html_colorvalues.asp
# You can also use Pantone colors or decimal or hexadecimal RGB values or CMYK values.
#    Pantone, CYMK:  http://blog.indika.net.id/html-color-codes-matching-chart-pantone-cmyk-rgb-hex/
#    Pantone:        http://www.theawristocrat.com/pantone.html
'''
legend1_color = "dodgerblue"           # HTML named colors
legend2_color = "deepskyblue"
legend3_color = "powderblue"
'''
'''
legend1_color = '#1133ff'              # RGB colors
legend2_color = "0x004466"             # Either single or double quotes is OK
legend3_color = 1234567                # Decimal or hex color values
'''
'''
legend1_color = (1, 0.4, 0.7)          # RGB colors 0-1
legend2_color = (0.5, 0.1, 0.2, 0.6)   # CMYK colors 0-1
legend3_color = (60, 44, 83)           # RGB or CMYK colors can also be 0-100
'''
'''
legend1_color = 'DodgerBlue'           # Mixed case is OK
legend2_color = [50, 10, 20]           # Use either [] around color value lists for 0-255 decimal numbers method
legend3_color = (0x6, 0x44, 0x30)      # Decimal or hex color values
'''
'''
legend1_color = 'PMS2945'              # Pantone Matching System (PMS) colors
legend2_color = 'P292'                 # PMS or P prefix
legend3_color = 'p2707'                # Either upper or lower case
'''

#moved into the main
#color = True   # Set to True or False

# Set light and dark values. The third bar will be shaded 1/2 way in the middle.
lightgray = 90      # Using percentage (0-100) method
darkgray  = 40

#if not color:
#    medgray = darkgray + ((lightgray - darkgray) / 2)
#    legend1_color = (medgray,   medgray,   medgray)
#    legend2_color = (lightgray, lightgray, lightgray)
#    legend3_color = (darkgray,  darkgray,  darkgray)
#else:
#    legend1_color = '#6989ff'
#    legend2_color = '#555555' #This is the grayscale version
#    legend3_color = '#999999' #This is the grayscale version


#legend1_text = "Percentile ratings of ICHE students tested who had never been institutionally educated, and who had been home educated three years or more."
#this change made in 2015
legend1_text = "Percentile ratings of Homeschool Idaho students tested who had been home educated three years or more."
legend2_text = "Percentile ratings of Homeschool Idaho students tested who had previously been institutionally educated, and who had been home educated two years or less."
legend3_text = "Percentile rating of all Idaho public school students tested on 2001 ITBS/TAP (latest scores available)."

# Each of the scores can be one of "ICHE_2yr", "ICHE_1yr", or a list of 6 score
# values. If one of the first two are used, data is pulled from the ICHE database.
# If a list of score values is used, they must be in the order:
# Composite, Vocabulary, Reading, Language, Mathematics, and Sources.
"""
2008:
scores1 = [83,90,88,78,74,76]  #"ICHE_2yr"           #[64,62,67,81,65,63]   # Dummy data
scores2 = [68,79,78,72,61,71]  #"ICHE_1yr"           #[74,52,57,61,75,83]   # Dummy data
scores3 = [54,52,57,51,55,53]
"""

'''
# 2009:
scores1 = [83,90,89,79,75,80]  #"ICHE_3yr"           #[64,62,67,81,65,63]   # Dummy data
scores2 = [79,77,77,66,81,77]  #"ICHE_2yr"           #[74,52,57,61,75,83]   # Dummy data
scores3 = [54,52,57,51,55,53]
'''

'''
#2010
scores1 = [81,89,88,78,72,76]  #"ICHE_3yr"           #[64,62,67,81,65,63]   # Dummy data
scores2 = [74,75,74,65,65,68]  #"ICHE_2yr"           #[74,52,57,61,75,83]   # Dummy data
scores3 = [54,52,57,51,55,53]
'''

'''
#2011
#C 81, 70  (from Median NE, SW lines)
#V 88, 74
#R 87, 70
#L 77, 65
#M 76, 72
#S 70, 63
scores1 = [81,88,87,77,76,70]  #"ICHE_3yr"           #[64,62,67,81,65,63]   # Dummy data
scores2 = [70,74,70,65,72,63]  #"ICHE_2yr"           #[74,52,57,61,75,83]   # Dummy data
scores3 = [54,52,57,51,55,53]
'''

#2012
#C 79, 75  (from Median NE, SW lines)
#V 85, 83
#R 85, 79
#L 77, 71
#M 67, 72
#S 74, 67
'''
scores1 = [79,85,85,77,67,74]
scores2 = [75,83,79,71,72,67]
scores3 = [54,52,57,51,55,53]
'''

#2013 (from Median NE, SW lines)
#C 80.0,80.0
#V 88.0,84.0
#R 85.0,85.0
#L 75.0,72.0
#M 67.5,66.0
#S 75.0,76.0

# 2013:
#Subject: 				Page 1 (SDC)	 	Page 2 (TRC)		Page 3 (TRA)
#Composite:  			93				80				80/78
#Vocabulary:  			97				88				88/84
#Reading:  				97				85				86/82
#Language:  			91				75				75/78
#Mathematics:  			77				67				67/69
#Sources:  				88				75				75/75

# scores1 = [80,88,86,75,67,75]
# scores2 = [78,84,82,78,69,75]
# scores3 = [54,52,57,51,55,53]

#2015 (from Median NE, SW lines)
# scores1 = [80,89,87,74,68,74]
# scores2 = [73,73,69,65,60,73]
# scores3 = [54,52,57,51,55,53]

#2016 (from Median NE, SW lines)
#NE
# 76.0, 87.0, 84.0, 72.0, 65.0, 69.0
#scores1 = [76,87,84,72,65,69]
#SW
# 77.0, 83.0, 82.5, 70.0, 61.0, 75.0
#scores2 = [77,83,83,70,61,75]
#scores3 = [54,52,57,51,55,53]

#2017 (from Median NE, SW lines)
#NE
#scores1 = [77,84,83,74,64,69]
#SW
#scores2 = [66,79,66,53,56,67]
#scores3 = [54,52,57,51,55,53]

#2018 (from Median NE, SW lines)
# in 2018 we switched to a newer version of the test
# results did not contain "Sources of Information", so I dropped it
#
#NE
#scores1 = [71,84,80,74,57]
#SW
#scores2 = [66,79,66,53,56]
#scores3 = [54,52,57,51,55]

#2019 (from Median NE, SW lines)
#NE
scores1 = [74,85,83,74,61]
#SW
scores2 = [66,79,66,53,56]
scores3 = [54,52,57,51,55]

chart_3D = True     # True or False (case-sensitive)

# End of file

