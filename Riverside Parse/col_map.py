
f = file('col_map.txt', 'w')

for i in range (104):
   f.write( str(i) + '   ')
   
   if i > 77:
      f.write('C')
   elif i > 51:   
      f.write('B')
   elif i > 25:
      f.write('A')
   
   f.write( '%c' % (ord('A') + (i % 26)) + '\n')
# 

f.close()