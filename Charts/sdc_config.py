#-------------------------------------------------------------------------------
# sdc_config.py
#
# School District Comparison
#-------------------------------------------------------------------------------

title      = "SCHOOL DISTRICT COMPARISON"

test_year  = 2019

subtitle1  = "Comparison of Homeschool Idaho"
subtitle2  = "State of Idaho School Districts, and National School Districts"
subtitle3  = "Iowa Tests of Basic Skills & Iowa Tests of Educational Development"
subtitle4  = "- " + str(test_year) + " -"


# The comment is placed under the chart and above the legend.
comment1    = "Percentile ratings based on overall ITBS/ITED performance of "+\
             "students on a district-by-district basis with Homeschool Idaho "+\
             "students and"
comment2   = "Idaho public school districts treated as single districts."

# Colors names you may use are most of the HTML color names. See
#    http://www.w3schools.com/HTML/html_colornames.asp
#legend1_color = "dodgerblue"
#legend2_color = "deepskyblue"
#legend3_color = "powderblue"

# Pantone Matching System (PMS) colors
#legend1_color = 'P267'              
#legend2_color = 'Pms2655'      # PMS or P prefix
#legend3_color = 'p2706'        # Either upper or lower case

# Hexadecimal colors
# Key: #rrggbb
# where rr = red, gg = green, bb = blue
# where range is 00-FF in hexadecimal (base 16, digits are 0-9, a,b,c,d,e,f -- either upper or lower case)
#    for example, after 59 comes 5A, 5B, 5B...; after 9F comes A0, A1, A2...
# where lower numbers are darker and higher numbers are lighter (00 = black, ff = white for each channel)
# A medium pure color wouild be one of #ff0000 (red), #00ff00 (green), and #0000ff (blue)
# To obtain lighter shades of the same color, increase the values of the other channels in lock step, e.g.
#  #0000ff -- medium blue
#  #4444ff -- lighter
#  #8888ff -- lighter still
#  #ffffff -- white

#moved into the main as a parameter
#color = False   # Set to True or False

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
#   #legend2_color = '#555555' #This is the grayscale version
#   #legend3_color = '#999999' #This is the grayscale version
#   #
#   legend2_color = '#99c6ff'
#   legend3_color = '#e3f0ff'

#
   
legend1_text = "HOME:  Percentile ratings of home educated students tested by "+\
               "Homeschool Idaho treated as a single district "+\
               "on " + str(test_year) + " ITBS/ITED."
legend2_text = "IDAHO:  Statewide percentile ratings of Idaho public school "+\
               "students treated as a single district on 2001 ITBS/TAP (latest "+\
               "scores available)."
legend3_text = "NATIONAL:  Nationwide percentile ratings of public school districts."

# Each of the scores can be one of "ICHE_2yr", "ICHE_1yr", or a list of 6 score
# values. If one of the first two are used, data is pulled from the ICHE database.
# If a list of score values is used, they must be in the order: 
# Composite, Vocabulary, Reading, Language, Mathematics, and Sources.
"""
# 2008:
scores1 = [99,99,97,95,87,93] #"ICHE_2yr"
scores2 = [56,48,59,50,56,52]
scores3 = [50,50,50,50,50,50]
"""
'''
# 2009:
scores1 = [97,98,97,94,87,93] #"ICHE_2yr"
scores2 = [56,48,59,50,56,52]
scores3 = [50,50,50,50,50,50]
'''
'''
# 2010:
scores1 = [95,98,97,93,84,91] #"ICHE_2yr"
scores2 = [56,48,59,50,56,52]
scores3 = [50,50,50,50,50,50]
'''
'''
# 2011:
#C 95, V 98, R 97, L 92, M 81, S 90
scores1 = [95,98,97,92,81,90] #"ICHE_2yr"
scores2 = [56,48,59,50,56,52]
scores3 = [50,50,50,50,50,50]
'''
'''
# 2012:
#C 92, V 96, R 95, L 86, M 76, S 88
scores1 = [92,96,95,86,76,88] #"ICHE_2yr"
scores2 = [56,48,59,50,56,52]
scores3 = [50,50,50,50,50,50]
'''

# 2013:
#Subject: 				Page 1 (SDC)	 	Page 2 (TRC)		Page 3 (TRA)
#Composite:  			93				80				80/78
#Vocabulary:  			97				88				88/84
#Reading:  				97				85				86/82
#Language:  			91				75				75/78
#Mathematics:  			77				67				67/69
#Sources:  				88				75				75/75

#2013
#scores1 = [93,97,97,91,77,88]
#scores2 = [56,48,59,50,56,52]
#scores3 = [50,50,50,50,50,50]

#2014
# scores1 = [92,96,96,89,76,85]
# scores2 = [56,48,59,50,56,52]
# scores3 = [50,50,50,50,50,50]

#2015
# scores1 = [93,97,93,91,77,88]
# scores2 = [56,48,59,50,56,52]
# scores3 = [50,50,50,50,50,50]

#2016
#C 92, V 96, R 95, L 86, M 76, S 88
# from Res
# Composite:  97.38
# Vocabulary:  96.18
# Reading:  94.13
# Language:  88.21
# Math:  76.06
# Sources: 84.51

#2017
#C 92, V 95, R 92, L 87, M 75, S 83
#scores1 = [92,95,92,87,75,83]
#scores2 = [56,48,59,50,56,52]
#scores3 = [50,50,50,50,50,50]

#2018
# in 2018 we switched to a newer version of the test
# results did not contain "Sources of Information", so I dropped it
#
# scores1 = [72,71,71,72,71]
# scores2 = [56,48,59,50,56]
# scores3 = [50,50,50,50,50]

#2019
#Composite
#Vocabulary
#Reading
#Written Expression (Language)
#Mathematics
scores1 = [73,86,75,74,61]
scores2 = [56,48,59,50,56]
scores3 = [50,50,50,50,50]

paper_size = "A4"   # Currently has no effect

chart_3D = True     # True or False (case-sensitive)

# End of file


