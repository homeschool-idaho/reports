#-------------------------------------------------------------------------------
# orm.py
#
# A home-brewed Object-Relational Mapper (ORM). But it's really just a one-way
# rel-obj map at the moment. And more of a translator than a mapper since tables
# and objects don't map well. So it's really a Relational-Object Translator or
# ROT -- code ROT. :)
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
      self.payment_id         = int(row[2])
      self.grade         = int(row[3])
      self.level         = int(row[4])
      try:
         self.campus        = row[5].strip()       # one of: 'N', 'E', 'W', 'S'
      except:
         self.campus     = '-'
      #
      self.campus = self.campus.upper()
      if self.campus not in 'NEWS':
         #raise Exception('Error -- campus is not one of "N", "E", "W", or "S"')
         pass
      #
      
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


# EOF

