#-------------------------------------------------------------------------------
# trc_config.py
#
# Test Results Comparison
#-------------------------------------------------------------------------------

title      = "TEST RESULTS COMPARISON"

test_year  = 2019

subtitle1  = "Homeschool Idaho"
subtitle2  = "Iowa Tests of Basic Skills & Iowa Tests of Educational Development"
subtitle3  = "- " + str(test_year) + " -"
subtitle4  = ""


# The comment is placed under the chart and above the legend.
comment1   = ""
comment2   = ""

# Colors names you may use are most of the HTML color names. See
#    http://www.w3schools.com/HTML/html_colornames.asp
#legend1_color = "dodgerblue"
#legend2_color = "deepskyblue"
#legend3_color = "powderblue"
#legend1_color = 'PMS2945'              # Pantone Matching System (PMS) colors
#legend2_color = 'P292'                 # PMS or P prefix
#legend3_color = 'p2707'                # Either upper or lower case

#moved into the main
#color = True   # Set to True or False

# Set light and dark values. The third bar will be shaded 1/2 way in the middle.
lightgray = 90      # Using percentage (0-100) method
darkgray  = 40

#if not color:
#   medgray = darkgray + ((lightgray - darkgray) / 2)
#
#   legend1_color = (medgray,   medgray,   medgray)
#   legend2_color = (lightgray, lightgray, lightgray)
#   legend3_color = (darkgray,  darkgray,  darkgray)
#
#else:
#   legend1_color = '#6989ff'
#   #swap these in and out for mixed version
#   legend2_color = '#555555' #This is the grayscale version
#   legend3_color = '#999999' #This is the grayscale version
#   #
#   #legend2_color = '#99c6ff' #this is the color version
#   #legend3_color = '#e3f0ff' #this is the color version
##


legend1_text = "HOME:  Percentile ratings of home educated students tested by "+\
               "Homeschool Idaho on " + str(test_year) + " ITBS/ITED."
legend2_text = "IDAHO:  Statewide percentile ratings of Idaho public school "+\
               "students on 2001 ITBS/TAP (latest scores available)."
legend3_text = "NATIONAL:  Nationwide percentile ratings of public school districts."


# Each of the scores can be one of "ICHE_2yr", "ICHE_1yr", or a list of 6 score
# values. If one of the first two are used, data is pulled from the ICHE database.
# If a list of score values is used, they must be in the order: 
# Composite, Vocabulary, Reading, Language, Mathematics, and Sources.
"""
2008:
scores1 = [82,90,88,78,74,76] #"ICHE_2yr"
scores2 = [54,52,57,51,55,53]
scores3 = [50,50,50,50,50,50]
"""

'''
# 2009:
scores1 = [83,90,88,79,75,79]
scores2 = [54,52,57,51,55,53]
scores3 = [50,50,50,50,50,50]
'''

'''
# 2010:
scores1 = [81,88,88,77,72,76]
scores2 = [54,52,57,51,55,53]
scores3 = [50,50,50,50,50,50]
'''
'''
# 2011:
# C 80, V 88, R 86, L 77, M 70, S 76
scores1 = [80,88,86,77,70,76]
scores2 = [54,52,57,51,55,53]
scores3 = [50,50,50,50,50,50]
'''
'''
# 2012:
# C 79, V 85, R 84, L 77, M 67, S 74
scores1 = [79,85,84,77,67,74]
scores2 = [54,52,57,51,55,53]
scores3 = [50,50,50,50,50,50]
'''

# 2013:
# 2013:
#Subject: 				Page 1 (SDC)	 	Page 2 (TRC)		Page 3 (TRA)
#Composite:  			93				80				80/78
#Vocabulary:  			97				88				88/84
#Reading:  				97				85				86/82
#Language:  			91				75				75/78
#Mathematics:  			77				67				67/69
#Sources:  				88				75				75/75
# scores1 = [80,88,85,75,67,75]
# scores2 = [54,52,57,51,55,53]
# scores3 = [50,50,50,50,50,50]

#2014
# scores1 = [78,88,84,74,67,71]
# scores2 = [54,52,57,51,55,53]
# scores3 = [50,50,50,50,50,50]

#2015 - ALL line from the Median
# scores1 = [79,88,85,73,67,74]
# scores2 = [54,52,57,51,55,53]
# scores3 = [50,50,50,50,50,50]

#2016 - ALL line from the Median
# 76.0, 87.0, 83.0, 72.0, 65.0, 69.0
#scores1 = [76,87,83,72,65,69]

#2017 - ALL line from the Median
# 77.0, 84.0, 81.0, 72.0, 64.0, 69.0
#scores1 = [77,84,81,72,64,69]
#scores2 = [54,52,57,51,55,53]
#scores3 = [50,50,50,50,50,50]

#2018 - ALL line from the Median
# in 2018 we switched to a newer version of the test
# results did not contain "Sources of Information", so I dropped it
#
# 77.0, 84.0, 81.0, 72.0, 64.0, 69.0
# scores1 = [70,83,80,73,56]
# scores2 = [54,52,57,51,55]
# scores3 = [50,50,50,50,50]

#2019
scores1 = [74,85,83,73,61]
scores2 = [54,52,57,51,55]
scores3 = [50,50,50,50,50]

chart_3D = True     # True or False (case-sensitive)

# End of file

