__author__ = 'markduenas'

# Python imports
import sys
import time

if __name__ == '__main__' :
   '''
   Expects a CSV string (no spaces) as input, e.g.:

   host=net.iche-idaho.org,user=iche,pwd=s1lvercreek,db=iche,rpt_year=2009,cachedDb=0

   IMPORTANT: The rpt_year is the year of testing; e.g. If you are running the report
              in 2010 for testing counts for 2011, use 2011 as the rpt_year.

   The last parameter is optional and defaults to False. The other are all
   required.
   '''
   startTime = time.time()

   # Time the report generation
   elapsedTime = time.time() - startTime
   timeStruct = time.gmtime(elapsedTime)
   timeStr = time.strftime('%M:%S', timeStruct)
   print 'Elapsed Time = ', timeStr

   print "Finished All"
   sys.exit(0)


#
# EOF
