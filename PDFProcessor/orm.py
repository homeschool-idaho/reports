#-------------------------------------------------------------------------------
# orm.py
#
# A home-brewed Object-Relational Mapper (ORM). But it's really just a one-way
# rel-obj map at the moment. And more of a translator than a mapper since tables
# and objects don't map well. So it's really a Relational-Object Translator or
# ROT; hence "Code ROT", heh, heh.
#
# Given a row of colums from a table, the constructors return an object containing
# those columns as attributes.
#
#-------------------------------------------------------------------------------

"""
class date:
   def __init__(self, inStr):
      self.year    = 0
      self.month   = 0
      self.date    = 0
      self.hours   = 0
      self.minutes = 0
      self.seconds = 0
      
      try:
         a = inStr
         dateTimeStr = inStr.strip()
         
         dateTimeParts = dateTimeStr.split(' ')
         
         dateParts  = dateTimeParts[0].split('-')
         self.year  = int(dateParts[0])
         self.month = int(dateParts[1])
         self.date  = int(dateParts[2])
         
         timeParts    = dateTimeParts[1].split(':')
         self.hours   = int(timeParts[0])
         self.minutes = int(timeParts[1])
         self.seconds = int(timeParts[2])
      except:
         pass
   #
   def __str__(self):
      return '-'.join([ str(self.year), str(self.month), str(self.date) ])
   #
   def __repr__(self):
      return self.__str__()
#
"""


MEMBER_COL_NAMES = ('member_id', 'mother_f_name', 'mother_l_name', 'father_f_name', 'father_l_name',
                    'street', 'city', 'state', 'zip', 'phone_home', 'phone_work', 'region', 'email',
                    'num_students', 'num_idcards', 'date_entered', 'date_modified', 'membership_expires',
                    'modified_by' )
NUM_MEMBER_COLS = len(MEMBER_COL_NAMES)
class member:
   def __init__(self, row):
      self.member_id     = int(row[0])
      self.mother_f_name = row[1].strip()
      self.mother_l_name = row[2].strip()
      self.father_f_name = row[3].strip()
      self.father_l_name = row[4].strip()
      self.street        = row[5].strip()
      self.city          = row[6].strip()
      self.state         = row[7].strip()
      self.zip           = row[8].strip()
      self.phone_home    = row[9].strip()   # aaabbbcccc
      try:
         self.phone_work = row[10].strip()   # aaabbbcccc
      except:
         self.phone_work = ''
      try:
         self.region     = int(row[11])
      except:
         self.region     = 0
      self.email         = row[12].strip()
      self.num_students  = row[13]               # int object has no strip()
      self.num_idcards   = row[14]               # int object has no strip()
      self.date_entered       = row[15]          # datetime.date object has no strip()
      self.date_modified      = row[16]          # datetime.date object has no strip()
      self.membership_expires = row[17]          # datetime.date object has no strip()
      self.modified_by        = row[18].strip()
   #
#


PAYMENT_COL_NAMES = ('payment_info_id', 'member_id', 'payment_id', 'item', 'amount', 'payment_type',
                     'date_entered', 'date_modified', 'modified_by', 'comment')
NUM_PAYMENT_COLS = len(PAYMENT_COL_NAMES)
class payment:
   def __init__(self, row):
      self.payment_id       = int(row[0])
      self.member_id        = int(row[1])
      try:
         self.payment_info_id  = int(row[2])
      except:
         self.payment_info_id  = 0
         
      self.item          = row[3].strip()   # one of: 'membership', 'membership refund',
                                            #         'donation', 'testing fee - new',
                                            #         'testing fee - returning', 'testing fee - refund'
      self.amount        = float(row[4])
      self.payment_type  = row[5].strip()   # one of: 'credit', 'cc', 'check'
      self.date_entered  = row[6]           # datetime.date object has no strip()
      self.date_modified = row[7]           # datetime.date object has no strip()
      self.modified_by   = row[8].strip()
      try:
         self.comment    = row[9].strip()
      except:
         self.comment    = 'n'
   #
#


STUDENT_COL_NAMES = ('student_id', 'member_id', 'f_name', 'l_name', 'm_init', 'dob', 'gender', 
                     'date_entered', 'date_modified', 'modified_by')
NUM_STUDENT_COLS = len(STUDENT_COL_NAMES)
class student:
   def __init__(self, row):
      self.student_id    = int(row[0])
      self.member_id     = int(row[1])
      self.f_name        = row[2].strip()
      self.l_name        = row[3].strip()
      try:
         self.m_init     = row[4].strip()
      except:
         self.m_init     = ''
      self.dob           = row[5]              # datetime.date object has no strip() -- MySqlDb returns a Python datetime object
      self.gender        = row[6].strip()      # one of: 'm', 'f'
      self.date_entered  = row[7]              # datetime.date object has no strip()
      self.date_modified = row[8]              # datetime.date object has no strip()
      self.modified_by   = row[9].strip()
   #
#


TESTING_HISTORY_COL_NAMES =  ('testing_history_id', 'student_id', 'payment_id', 'grade', 'level',
                              'campus', 'test_type', 'region', 'test_year', 'years_hs', 'years_ps',
                              'returning', 'self.proctor', 'canceled', 'summa', 'dual', 'whos_who',
                              'date_entered', 'date_modified', 'comment')
NUM_TESTING_HISTORY_COLS = len(TESTING_HISTORY_COL_NAMES)
class testing_history:
   def __init__(self, row):
      self.testing_history_id = int(row[0])
      self.student_id         = int(row[1])
      try:
         self.payment_id         = int(row[2])
      except:
         self.payment_id = 0
      self.grade         = int(row[3])
      self.level         = int(row[4])
      self.campus        = row[5].strip()       # one of: 'N', 'E', 'W', 'S'
      self.test_type     = row[6].strip()       # one of: 'ITBS', 'ITED'
      try:
         self.region     = int(row[7])
      except:
         self.region     = 0
      self.test_year     = int(row[8])
      self.years_hs      = int(row[9])
      self.years_ps      = int(row[10])
      self.returning     = row[11].strip()      # one of: 'y', 'n'
      self.proctor       = row[12].strip()
      try:
         self.canceled   = row[13].strip()
      except:
         self.canceled   = None
      try:
         self.summa      = row[14].strip()      # one of: 'y', 'n'
      except:
         self.summa      = 'n'
      self.dual          = row[15].strip()      # one of: 't', 'f'
      try:
         self.whos_who   = row[16].strip()      # one of: 'y', 'n'
      except:
         self.whos_who   = 'n'
      self.date_entered  = row[17]              # datetime.date object has no strip()
      self.date_modified = row[18]              # datetime.date object has no strip()
      try:
         self.comment    = row[19].strip()
      except:
         self.comment    = ''
   #
#


ITBS_SCORE_DATA_COL_NAMES =  (
   'score_id', 'vocabulary', 'reading_compreh', 'reading_total', 'word_analysis',
   'listening', 'spelling', 'capitalization', 'punct_read_word', 'usage_expression',
   'language_total', 'concepts_est', 'prob_data_interp', 'mathT_mComput', 'computation',
   'mathT_pComput', 'coreT_mComput', 'coreT_pComput', 'social_studies', 'science',
   'maps_diagrams', 'ref_mtrls', 'sources_total', 'composite_mComput', 'composite_pComput', 
   'filler_25', 'filler_26', 'rdProfileT_pWords', 'rdProfileT_mWords', 'filler_29', 
   'filler_30')
NUM_ITBS_SCORE_DATA_COLS = len(ITBS_SCORE_DATA_COL_NAMES)
class itbs_score_data:
   def __init__(self, row):
      self.score_id          = float(row[ 0])
      self.vocabulary        = float(row[ 1])
      self.reading_compreh   = float(row[ 2])
      self.reading_total     = float(row[ 3])   # Reading Total
      self.word_analysis     = float(row[ 4])
      self.listening         = float(row[ 5])
      self.spelling          = float(row[ 6])
      self.capitalization    = float(row[ 7])
      self.punct_read_word   = float(row[ 8])
      try:
         self.usage_expression = float(row[ 9])
      except:
         print 'Error; usage_expression =', row[9], ' for score_id', row[ 0]
         self.usage_expression = 0
      #
      self.language_total    = float(row[10])   # Language Total
      self.concepts_est      = float(row[11])
      self.prob_data_interp  = float(row[12])   # ITBS Prob Solve slot
      self.mathT_mComput     = float(row[13])   # ITED Prob Solve slot
      self.computation       = float(row[14])
      self.mathT_pComput     = float(row[15])   # Math Total
      self.coreT_mComput     = float(row[16])
      self.coreT_pComput     = float(row[17])   # Core Total
      self.social_studies    = float(row[18])
      self.science           = float(row[19])
      self.maps_diagrams     = float(row[20])
      self.ref_mtrls         = float(row[21])
      self.sources_total     = float(row[22])
      self.composite_mComput = float(row[23])
      self.composite_pComput = float(row[24])   # Composite
      self.filler_25         = float(row[25])
      self.filler_26         = float(row[26])
      self.rdProfileT_pWords = float(row[27])
      self.rdProfileT_mWords = float(row[28])
      self.filler_29         = float(row[29])
      self.filler_30         = float(row[30])
   #
#


ITED_SCORE_DATA_COL_NAMES =  (
   'score_id', 'vocabulary', 'reading_compreh', 'reading_total', 'filler_4',
   'filler_5', 'spelling', 'filler_7', 'filler_8', 'filler_9', 'revise_writ_mtrl',
   'filler_11', 'filler_12', 'concepts_probs', 'computation',
   'mathT_pComput', 'coreT_mComput', 'coreT_pComput', 'social_studies', 'science',
   'filler_20', 'filler_21', 'sources_of_info', 'composite_mComput', 'composite_pComput', 
   'filler_25', 'filler_26', 'filler_27', 'filler_28', 'filler_29', 'filler_30')
NUM_ITED_SCORE_DATA_COLS = len(ITED_SCORE_DATA_COL_NAMES)
class ited_score_data:
   def __init__(self, row):
      self.score_id          = float(row[ 0])
      self.vocabulary        = float(row[ 1])
      self.reading_compreh   = float(row[ 2])
      self.reading_total     = float(row[ 3])   # Reading Total
      self.filler_4          = float(row[ 4])
      self.filler_5          = float(row[ 5])
      self.spelling          = float(row[ 6])
      self.filler_7          = float(row[ 7])
      self.filler_8          = float(row[ 8])
      try:
         self.filler_9       = float(row[ 9])
      except:
         print 'Error; filler_9 =', row[9], ' for score_id', row[ 0]
         self.filler_9       = 0
      #
      self.revise_writ_mtrl  = float(row[10])   # Language Total slot if we were on ITBD (This is ITED)
      self.filler_11         = float(row[11])
      self.filler_12         = float(row[12])   # ITBS Prob Solve slot
      self.concepts_probs    = float(row[13])   # ITED Prob Solve slot
      self.computation       = float(row[14])
      self.mathT_pComput     = float(row[15])   # Math Total
      self.coreT_mComput     = float(row[16])
      self.coreT_pComput     = float(row[17])   # Core Total
      self.social_studies    = float(row[18])
      self.science           = float(row[19])
      self.filler_20         = float(row[20])
      self.filler_21         = float(row[21])
      self.sources_of_info   = float(row[22])
      self.composite_mComput = float(row[23])
      self.composite_pComput = float(row[24])   # Composite
      self.filler_25         = float(row[25])
      self.filler_26         = float(row[26])
      self.filler_27         = float(row[27])
      self.filler_28         = float(row[28])
      self.filler_29         = float(row[29])
      self.filler_30         = float(row[30])
   #
#


SCORE_STUDENT_DATA =  ('testing_history_id', 'score_id', 'member_id', 'student_id', 
                       'l_name', 'f_name', 'gender', 'dob', 'grade', 'level', 
                       'date_tested', 'test_type', 'region_name', 'region_num',
                       'campus', 'state', 'nat_id')
NUM_SCORE_STUDENT_DATA_COLS = len(SCORE_STUDENT_DATA)
class score_student_data:
   def __init__(self, row):
      try:
         self.testing_history_id = int(row[ 0])
      except:
         #print 'Error; testing_history_id =', row[0], ' for student_id', row[ 3],row[ 5],row[ 4], 'tested', row[10]
         self.testing_history_id = 0
      #
      self.score_id           = int(row[ 1])
      self.member_id          = int(row[ 2])
      self.student_id         = int(row[ 3])
      self.l_name             = str(row[ 4]).strip()
      self.f_name             = str(row[ 5]).strip()
      self.gender             = str(row[ 6]).strip()
      self.dob                = str(row[ 7]).strip()
      self.grade              = int(row[ 8])
      self.level              = int(row[ 9])
      self.date_tested        = str(row[10]).strip()
      self.test_type          = str(row[11]).strip()
      self.region_name        = str(row[12]).strip()
      self.region_num         = int(row[13])
      self.campus             = str(row[14]).strip()
      self.state              = str(row[15]).strip()
      self.nat_id             = str(row[16]).strip()
      
      #if self.score_id == 313:
      #   print 'Bad usage_expr "K.7" in score_grade_equiv Riverside data for', self.f_name, self.l_name, ', student_id', self.student_id, ', nat_id', self.nat_id
      #
   #
#

# EOF

