


class Enum:
	"""
	Python has no enum, so this makes some from a CSV list of strings.
	Usage: if 'prefix' arg is 'my' and 'colNamesCSV' arg contains 'zero,one,two',
	then the generated enums are my.zero, my.one, and my.two. These are placed at
	global scope.
	"""
	def MakeEnums(self, prefix, colNamesCSV):
		exec 'class ' + prefix + ': pass'
		exec 'print str(' + str(prefix) + ')'   # DEBUG

		colNames = colNamesCSV.split(',')
		for i in range( len(colNames) ):
			cmd = prefix + '.' + colNames[i] + '=' + str(i)
			print cmd   # DEBUG
			exec cmd
		#
	#
#
e = Enum()


#-------------------------------------------------------------------------------
# Make MySQL table column names as enums
#-------------------------------------------------------------------------------

# Student Personal Data. Test type is itbs or ited. Riverside data has region 
# number and name combined as Building Name; has campus as Class Name.
stuDataCols = 'testing_history_id,score_id,member_id,student_id,l_name,f_name,'+\
				'gender,dob,grade,level,date_tested,test_type,region_num,'+\
				'region_name,campus,state'
e.MakeEnums( 'stuData', stuDataCols)

# Score types:
#    Raw Scores     
#    Standard Score
#    Grade Equivalent
#    National Percentile Rank (NPR)
#    Normal Curve Equivalents (NCE)
#    National Stanine
# Use the same columns for all score tables.
score_cols = 'score_id,vocabulary,reading_comp,reading_total,filler_4,filler_5,'+\
'spelling,capital,punct,usage_expr,lang_total,concepts_est,itbs_prov_solv,'+\
'ited_prob_solv,computation,math_total,filler_16,core_total,social_studies,'+\
'science,maps_diag,ref_matrl,info_src,filler_23,composite,filler_25,filler_26,'+\
'filler_27,filler_28,filler_29,filler_30'
e.MakeEnums('score', score_cols)



