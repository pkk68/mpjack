#!/usr/bin/env python3
"""
Jackpot ruler for hints

This script extracts vietlott winning numbers and
   generates a list of top or pot potential numbers


Revision:
   v1.04.230818 - Bugfix: duplication in random.sample
   v1.04.170801 - power 6/55 support
   v1.03.170504 - Next new 6-line from bottom of result file
   v1.02.170419 - Refactor to get familiar with pylint
   v1.01.170330 - Changed revision to yymmdd rev.20170330-144143
   v1.01.033017 - Bugfix blank line rev.20170330-144143
   v1.01.031517 - New random number list
   v1.00.010617 - First release for both python 2&3

Ref:
   - http://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/
   https://vietlott.vn/en/trung-thuong/ket-qua-trung-thuong/645
   https://vietlott.vn/en/trung-thuong/ket-qua-trung-thuong/655   

"""
# Python 2 and 3:
# SyntaxError: invalid syntax for print without newline
from __future__ import print_function



import os
import sys
import copy
import mmap
import time
import random
import logging
import datetime
import requests
from bs4 import BeautifulSoup


###################
# General Globals #
###################
#
# Mega45 layout map
#
MEGA45 = ["01", "02", "03", "04", "05", \
          "06", "07", "08", "09", "10", \
          "11", "12", "13", "14", "15", \
          "16", "17", "18", "19", "20", \
          "21", "22", "23", "24", "25", \
          "26", "27", "28", "29", "30", \
          "31", "32", "33", "34", "35", \
          "36", "37", "38", "39", "40", \
          "41", "42", "43", "44", "45"]

JACKPOT_MIN = 1
JACKPOT_MAX = 45
JACKPOT_SIX = 6
JACKPOT_LEN = 18

# power 6/55
# power = True
# Power55 layout map
#
POWER55= ["01", "02", "03", "04", "05", \
          "06", "07", "08", "09", "10", \
          "11", "12", "13", "14", "15", \
          "16", "17", "18", "19", "20", \
          "21", "22", "23", "24", "25", \
          "26", "27", "28", "29", "30", \
          "31", "32", "33", "34", "35", \
          "36", "37", "38", "39", "40", \
          "41", "42", "43", "44", "45", \
          "46", "47", "48", "49", "50", \
          "51", "52", "53", "54", "55"]

POWERJACK_MAX = 55

debug = True
#debug = False   # No debug printout

# for guest to choose random blue ball or red ball
# Blue ball marked as number 1
# Red ball marked as number 2
blue_ball = True
global_seed = 0
power_only = 0   # for Power55

# Python 2 i.e: Linux
# Python 3 i.e: Python for Windows and others
#python2 = True
python3 = True

numcount = []
pnumcount = []
toplist =[]
potlist = []
TopPotList = []
pTopPotList = []
savenewtop =[]
savenewpot = []





#--------------------------------------------------------------------------
def dbp(msg=""):
   print(f"DEBUG#{sys._getframe().f_back.f_lineno}: {msg}")
   return None
def dprint(s):
   "This prints a passed string into this function"
   global debug
   debug = False   # No debug printout
   if debug is True:
      print(s)
   return None
#--------------------------------------------------------------------------
def is_python2():
   "This will check and set current python version at the run time"
   global python2
   if sys.version_info[0] == 3:
      python2 = False
   return None
#--------------------------------------------------------------------------
def usage():
   "How to use"""
   print("USAGE: ")
   print("    ./mpjack.py ")
   print("EXAMPLE: ")
   print("    python mpjack.py ")
   return None

#--------------------------------------------------------------------------
def convert_line_to_number(l):
   """Convert numbers in one line to a list"""

   alist = []
   tmp = l[0]+l[1]
   dprint(tmp)
   alist.append(tmp)

   tmp = l[3]+l[4]
   dprint(tmp)
   alist.append(tmp)

   tmp = l[6]+l[7]
   dprint(tmp)
   alist.append(tmp)

   tmp = l[9]+l[10]
   dprint(tmp)
   alist.append(tmp)

   tmp = l[12]+l[13]
   dprint(tmp)
   alist.append(tmp)

   tmp = l[15]+l[16]
   dprint(tmp)
   alist.append(tmp)

   return alist
#--------------------------------------------------------------------------
def process(power55, l):
   """
      Extract one line to a list of number

        Parameters:
           l  - list of number per line

        Return Values:
           None

   """
   assert l is not None
   logger = logging.getLogger(__name__)
   #
   #'01 02 03 04 05 06' with length = 18 (or 19 with \n)
   #
   if len(l) < JACKPOT_LEN or len(l) < JACKPOT_LEN - 1:
      dprint(len(l))
      dprint("Blank line or Empty!!!")
      #
      # ERROR: Blank line
      #
      #Traceback (most recent call last):
      #  File "./inJackpot.py", line 533, in <module>
      #    main()
      #  File "./inJackpot.py", line 418, in main
      #    process(line)
      #  File "./inJackpot.py", line 90, in process
      #    tmp = l[0]+l[1];
      #IndexError: string index out of range
      logging.warning(l)
      logging.warning(len(l))
      logging.warning('Blank line!!!')
      return None

   alist = convert_line_to_number(l)
   #dbp(alist)

   global numcount
   global pnumcount

   if power55 is True:
      i = 1
      if not pnumcount:
         pnumcount = [0]
         while i < POWERJACK_MAX:
            pnumcount.append(0)
            i += 1
      dprint(len(pnumcount))      
   else:
      i = 1
      if not numcount:
         numcount = [0]
         while i < JACKPOT_MAX:
            numcount.append(0)
            i += 1
      dprint(len(numcount))

   i = 1
   mloc = 0
   ploc = 0
   dprint(alist)
   logging.info(alist)
   for i in alist:
      pcounter = 0
      mcounter = 0
      if power55 is True:
         if str(i) in POWER55:
            ploc = POWER55.index(str(i))
            pcounter += 1

         pnumcount[ploc] += pcounter
         #print("pnumcount[%d] = %d" % (ploc, pnumcount[ploc]))
         tmp_numcount = pnumcount
      else:
         if str(i) in MEGA45:
            mloc = MEGA45.index(str(i))
            mcounter += 1

         numcount[mloc] += mcounter
         #print("numcount[%d] = %d" % (mloc, numcount[mloc]))
         tmp_numcount = numcount

   #dbp(tmp_numcount)
   logging.info(tmp_numcount)
   return tmp_numcount

#--------------------------------------------------------------------------
def get_potop(power55, numbercounter, potcounter, filename):
   """
   Get current top and pot from current input list
   """
   logger = logging.getLogger(__name__)
   global toplist
   global potlist
   global TopPotList
   global pTopPotList
   #global savenewtop
   #global savenewpot
   # Big list to collect all the top, pot numbers
   # We have an option to pick up 6-number `potop`
   tmp_numcount = []
   ttoplist = []

   # Top1 and Pot1 main handler
   savenumpot = copy.deepcopy(potcounter)
   #savenumpot = copy.deepcopy(numbercounter)
   #dbp(numbercounter)
   #dbp(potcounter)
   logging.info('Calculating top list...')
   logging.debug(numbercounter)
   ttoplist = get_top(numbercounter, ttoplist)
   write_file(filename, "Top:", ttoplist)
   #dbp(ttoplist)
   logging.debug("ttoplist")
   logging.debug(ttoplist)
   
   #new top list
   logging.info('Saved new top list')
   tmp_numcount = copy.deepcopy(numbercounter)
   logging.debug(tmp_numcount)
   savenewtop_local = tmp_numcount
   logging.debug(savenewtop_local)
   #dbp(savenewtop_local)
   
   #logging.info('Done to backup top1 in result file')
   #save to new TopPotList
   if power55 is True:
      dprint("Power55")
      pTopPotList += ttoplist
   else:
      dprint("Mega45")
      TopPotList += ttoplist
   toplist = ttoplist
   #dbp(ttoplist)

   ppotlist = []
   logging.info('Calculating pot list...')
   ppotlist = get_pot(savenumpot, ppotlist)
   write_file(filename, "Pot:", ppotlist)
   #dbp(ppotlist)
   savenewpot_local = copy.deepcopy(savenumpot)
   #dbp(savenewpot_local)
   logging.debug(savenewpot_local)
   
   #Continuing to save to new TopPotList
   if power55 is True:
      pTopPotList += ppotlist
   else:
      TopPotList += ppotlist
   potlist = ppotlist
   #logging.info('Done to backup pot1 in result file')
   logging.debug(numbercounter)
   logging.debug(tmp_numcount)
   #dbp(numbercounter)
   return tmp_numcount, savenewtop_local, savenewpot_local
#--------------------------------------------------------------------------
def get_top(numtop, toplist):
   """
       Get index (mega number) from number of occurences in toplist
         Parameters:
            numtop  - number of occurences
            toplist - a list of mega number (incl occurences)

         Return Values:
            a list of mega number

   """
   logger = logging.getLogger(__name__)
   assert numtop is not None
   #dbp(numtop)
   
   # Win32 python3
   # TypeError: 'NoneType' object is not iterable
   # This is end of file 
   top = max(numtop)
   #sequence = numtop.count(top)
   #print("max value: ", top)
   #print("seq value: ", sequence)
   toplist = []
   #nnext = 0
   for t in numtop:
      if t == top:
         dprint(t)
         numtoplist = numtop.index(t) + 1
         #dbp(numtoplist)
         toplist.append(numtoplist)
         # reset
         numtop[numtoplist - 1] = -1
         #nnext += 1
         continue
   #dbp(toplist)
   logging.info("toplist")
   logging.info(toplist)
   return toplist
#--------------------------------------------------------------------------
def get_pot(numpot, potlist):
   """
       Get index (mega number) from number of occurences in potlist
         Parameters:
            numpot  - number of occurences
            potlist - a list of mega number (incl occurences)

         Return Values:
            a list of mega number

   """
   logger = logging.getLogger(__name__)
   assert numpot is not None
   #dbp(numpot)
   pot = min(numpot)
   #sequence = numpot.count(pot)
   #print("min value: ", pot)
   #print("seq value: ", sequence)
   potlist = []
   #nnext = 0
   for t in numpot:
      if t == pot:
         dprint(t)
         numpotlist = numpot.index(t) + 1
         #print("min index: ", numpotlist)
         potlist.append(numpotlist)
         # reset
         numpot[numpotlist -1] = 999
         #nnext += 1
         continue
   #dbp(potlist)
   logging.info("potlist")
   logging.info(potlist)
   return potlist
#--------------------------------------------------------------------------
def is_new_number_string(url):
   """
      Check Vietlott homepage to fetch the latest jackpot number result
        Parameters:
           url  - Vietlott homepage

        Return Values:
           1       - No new number
           jackpot - Found new jackpot
   """
   #from bs4 import BeautifulSoup
   logger = logging.getLogger(__name__)
   if python2 is False:
      # In python3, urllib2 has been split into urllib.request and urllib.error
      # urllib2 is no longer used. Try using urllib.request.
      # https://docs.python.org/2/library/urllib2.html#module-urllib2
      from urllib.request import urlopen
      from urllib.error import URLError, HTTPError
   else:
      # Not Python 3 - today, it is most likely to be Python 2
      # But note that this might need an update when Python 4
      # might be around one day
      from urllib import urlopen
      from urllib2 import URLError, HTTPError
   dbp(url)
   newnumber = 0
   try:
      #vietlottpage = urllib.urlopen(url)
      vietlottpage = urlopen(url)
   except gaierror as inst:
      print("WARNING:", " %s \n" % inst.strerror)
      print("Reason: ", inst.reason)
      logging.warning(inst.strerror)
      logging.warning(inst.reason)
      pass
   except HTTPError as inst:
      print("WARNING:", " %s \n" % inst.strerror)
      print("Error code: ", inst.code)
      logging.warning(inst.code)
      logging.warning(inst.strerror)
      pass
   except URLError as inst:
      print("WARNING:", " %s \n" % inst.strerror)
      print("Reason: ", inst.reason)
      logging.warning(inst.reason)
      logging.warning(inst.strerror)
      pass
   else:
      #print("WARNING: No connection!\n")
      pass
   user_agents = [ 
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 
	'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148', 
	'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36' 
   ] 
   user_agent = random.choice(user_agents) 
   headers = {'User-Agent': user_agent}   
   s = requests.session()
   cookie_obj = requests.cookies.create_cookie(domain="example.com",name="COOKIE_NAME",value="the cookie works")
   s.cookies.set_cookie(cookie_obj)   
   r=s.get(url, headers=headers)
   #r=requests.get(url)
   #print(r.url)
   #print(r.status_code)
   #dbp(r)
   #print(r.text)
   #print(r.content)
   #print(r.json()['headers']['User-Agent']) 
   #print(r.headers)
   #utf-8,gbk
   #print(r.encoding)
   #print(r.cookies)
   #print(r.text)
   #print(s.cookies.get_dict())
   #dbp()
   
   # Python.s html.parser
   soup = BeautifulSoup(r.content, "html.parser")
   #soup = BeautifulSoup(vietlottpage.read(), "html.parser")
   if len(soup) == 0 or soup is None:
      logging.critical("Failed to use BeautifulSoup to parse vlott url")
      return 0
   #dbp(soup)
   soup.find_all("div", class_="sister")   
   #estimated_money = 'jackpot-win'
   estimated_money = 'so_tien'
   Jtotal = soup.find('div', attrs={'class': estimated_money})
   #
   # TypeError: object of type 'NoneType' has no len()
   #
   #if len(Jtotal) == 0 or Jtotal is None:
   if Jtotal is None:
      print("WARNING: Check connection please!\n")
      logging.warning('jackpot-win:Check connection please!')
   else:
      #dprint(Jtotal)
      tmpstr = Jtotal.text.strip()
      tmpstr = tmpstr.encode('ascii', errors='ignore')
      print(tmpstr)
      # In python v3.5.2 Windows 6.3 build 9600
      # UnicodeEncodeError: 'charmap' codec can't encode
      # character '\u0111' in position 174:
      # character maps to <undefined>
      logging.warning(tmpstr)
      #logging.info(tmpstr)
   newnumber = 0
   estimated_number = 'result-number'
   content = soup.find('ul', attrs={'class': estimated_number})
   #if len(content) == 0 or content is None:
   if content is None:
      #print("Check connection please!")
      logging.warning('result-number:Check connection please!')
   else:
      tmpstr = content.text.strip()
      newnumber = tmpstr.replace("\n", " ")
      logging.info(newnumber)
   return newnumber
#--------------------------------------------------------------------------

def mega45_check_result(resultfile):
   """Update result file if needed"""
   logger = logging.getLogger(__name__)
   # From 10-Aug-2023
   # https://vietlott.vn/en/trung-thuong/ket-qua-trung-thuong/645
   # https://vietlott.vn/en/trung-thuong/ket-qua-trung-thuong/655
   url = 'https://vietlott.vn/'
   new = is_new_number_string(url)
   #dprint(new)
   if new == 0:
      logging.error("ERROR: Something wrong here!")
      logging.error("using outdated local database")
      return True
    
   # May raise IOError
   handle = open(resultfile)
   try:
      # May raise UnicodeDecodeError
      data = handle.read()
   except IOError as inst:
      print("error:", "%s: %s \n" % (resultfile, inst.strerror))
      logging.error(inst.strerror)
      return False
   finally:
      handle.close()

   #if new in open(resultfile).read():
   if new in data:
      #do nothing
      #No need to update result to file
      #print(".")
      logging.warning('No need to update result to file!')
      #logging.critical('No need to update result to file!')
   else:
      u = 'Updating...'
      print(u)
      logging.info(u)
      f = open(resultfile, 'a')
      try:
         f.write(new)
         f.write('\n')
      finally:
         f.close()
      s = '...........succeed'
      print(s)
      logging.info(s)
   return True
#--------------------------------------------------------------------------
# top output file
def write_file(ofile, prefix, string):
   """Write file wrapper"""
   logger = logging.getLogger(__name__)
   if os.path.isdir(ofile):
      print("error:", '%s: file not found \n' % ofile)
      file(ofile, 'w').close()
   try:
      # Open a file
      ticket_file = open(ofile, "a")
      #print("Name of the file: ", ofile)
   except IOError as inst:
      print("error:", "%s: %s \n" % (ofile, inst.strerror))
      logging.error(inst.strerror)
   else:
      line = "%s %s; \n" % (prefix, string)
      ticket_file.write(line)
   finally:
      # Close opened file
      ticket_file.close()
      #return False

   return True
#--------------------------------------------------------------------------
def add_prefix_zero_to_number(rlist):
   """Add 0 to number < 10 in list"""

   assert rlist is not None
   #logger = logging.getLogger(__name__)
   #dbp(rlist)
   if len(rlist) == JACKPOT_SIX:
      tmplist = quicksort(rlist)
   else:
      # Power55's jackpot 2 processing
      # Only quick sort first six elements
      rs = quicksort(rlist[:6])
      #dbp(rs)
      rs.append(rlist[6])
      tmplist = rs
   #dbp(tmplist)
      
   rlistFinal = []
   strnum = None
   for num in tmplist:
      if num < 10:
         strnum = '0' + str(num)
      else:
         strnum = str(num)
      rlistFinal.append(strnum)
      
   #dbp(rlistFinal)
   return rlistFinal
#--------------------------------------------------------------------------
def preparation(power55):
   """All prepraration actions"""
   logger = logging.getLogger(__name__)

   jacktype = MEGA45
   if power55 is True:
       jacktype = POWER55

   global blue_ball
   global global_seed
   # Initialize internal state of the random number generator.
   # vlott chose 3 random guest i.e: students at university, college
   random.seed()
   # MC randomly chooses one guest for ball
   random_guest = random.choice([1, 2, 3])
   # 64800 is total seconds from/at 18:00:00 clock
   # 65401 is total seconds from/at 18:10:01 clock
   seed = random.uniform(64800 + random_guest, 65401 + random_guest)
   logging.info("Randomize the global seed by guest")
   logging.info(seed)
   global_seed = int(seed)
   logging.info(global_seed)
   if global_seed % 2:
      blue_ball = False
      logging.info("This time for RED(2) ball")
   else:
      logging.info("This time for BLUE(1) ball")
   logging.info("End of randomize the seed by guest")

   # Governor seed
   logging.info("Randomize the seed by governor")
   # MC randomly chooses one guest for ball
   random_governor = random.choice([1, 2, 3, 4, 5, 6])
   r1 = random.SystemRandom(random_governor).choice(jacktype)
   logging.info("random governor")
   logging.info(random_governor)
   logging.info(int(r1))
   # Governor is testing... 
   r = []
   if int(r1) % 2:
      r = get_random_sample(power55, jacktype)
   else:
      # randomize numbers by using randint() function
      r = get_random(power55)
   logging.info("Draw test")
   logging.info(r)
   logging.info("End of randomize the seed by governor")
   print("Draft test: ", r)
   return True
#--------------------------------------------------------------------------
def get_random_sample(p55, input_list):
   """Generate random 6-number jackpot using sample function"""
   logger = logging.getLogger(__name__)
   dprint("Getting random sample")

   r = []
   ilist = input_list
   while len(r) < JACKPOT_SIX:
      num = random.choice(ilist)
      if num not in r:
         r.append(num)
         ilist.remove(num)

   if p55 is True:
      num = random.choice(ilist)
      r.append(num)
      
   del ilist
   #dbp(r)
   return r
#--------------------------------------------------------------------------
def get_random(jtype):
   """Generate random 6-number jackpot using randint function"""
   logger = logging.getLogger(__name__)
   dprint("Getting random list")
   #total_number = ['one', 'two', 'three', 'four', 'five', 'six']
   jacktype = MEGA45
   maxx = JACKPOT_MAX
   if jtype is True:
       jacktype = POWER55
       maxx = POWERJACK_MAX

   global blue_ball

   r = []
   tmp = 99
   stop = False
   counter = 0
   #while (stop == 0 or counter > JACKPOT_SIX):
   while stop is False:
      #Bug #001
      #345 CRITICAL: Number duplication
      #346 CRITICAL:7
      #347 CRITICAL:[27, 36, 27, 43, 19, 12]
      #348 CRITICAL: Done to save number duplication
      i = 0
      while i < JACKPOT_SIX:
         if blue_ball is False:
            # Auto generate new integer
            tmp = random.randint(JACKPOT_MIN, maxx)
         else:
            # Auto generate new integer
            tmp = random.randrange(JACKPOT_MIN, maxx, 1)
         if tmp not in r:
            # Add new number to current list
            r.append(tmp)
            i = i + 1
         # Reset
         tmp = 99
      #dbp(r)
      for ii in r:
         total = r.count(ii)
         #print("total=", total)
         counter += total
         dprint(counter)
         if total == 1 and counter <= JACKPOT_SIX:
            # STOP now
            stop = True
         else:
            logging.critical('ERROR: Number duplication')
            logging.critical(counter)
            logging.critical(total)
            logging.critical(ii)
            logging.critical(r)
            logging.critical(stop)
            logging.critical('ERROR: Done to save number duplication')
            # Empty number list
            if len(r) >= JACKPOT_SIX:
               #dbp(r)
               r = []
               counter = 0
               stop = False
               
   #dbp(r)
   if jtype is True:
      i = 0
      # One more number for power55 jackpot 2
      while i == 0:
         if blue_ball is False:
            # Auto generate new integer
            tmp = random.randint(JACKPOT_MIN, maxx)
         else:
            # Auto generate new integer
            tmp = random.randrange(JACKPOT_MIN, maxx, 1)
         if tmp not in r:
            # Add new number to current list
            #dbp(tmp)
            r.append(tmp)
            i = i + 1     
   return add_prefix_zero_to_number(r)
#--------------------------------------------------------------------------
def quicksort(arr):
   """Sorting numbers in list input"""

   if len(arr) <= 1:
      return arr
   #
   # Python 3 Win32:
   # TypeError: list indices must be integers or slices, not float
   #
   pivot = arr[int(round(len(arr) / 2))]
   left = [x for x in arr if x < pivot]
   middle = [y for y in arr if y == pivot]
   right = [z for z in arr if z > pivot]
   return quicksort(left) + middle + quicksort(right)
#--------------------------------------------------------------------------
def get_random_main(power55):
   """Random main generator"""
   logger = logging.getLogger(__name__)

   sort = True

   jacktype = MEGA45
   if power55 is True:
       jacktype = POWER55

   global blue_ball
   # Initialize internal state of the random number generator.
   # vlott chose 3 random guest i.e: students at university, college
   random.seed()
   # MC randomly chooses one guest for ball
   random_guest = random.choice([1, 2, 3])
   # 64800 is total seconds from/at 18:00:00 clock
   # 65401 is total seconds from/at 18:10:01 clock
   seed = random.uniform(64800 + random_guest, 65401 + random_guest)
   logging.info("Randomize the seed by guest")
   logging.info(seed)
   logging.info(int(seed))
   if int(seed) % 2:
      blue_ball = False
      logging.info("This time for RED(2) ball")
   else:
      logging.info("This time for BLUE(1) ball")
   logging.info("End of randomize the seed by guest")

   # Governor seed
   logging.info("Randomize the seed by governor")
   # MC randomly chooses one guest for ball
   random_governor = random.choice([1, 2, 3, 4, 5, 6])
   r1 = random.SystemRandom(random_governor).choice(jacktype)
   logging.info("random governor")
   logging.info(random_governor)
   logging.info(int(r1))
   # Governor is testing... 
   r = []
   if int(r1) % 2:
      ts = MEGA45
      if power55 is True:
         ts = POWER55
      r = get_random_sample(power55, ts)
   else:
      # randomize numbers by using randint() function
      r = get_random(power55)
      #dbp(r)
   logging.info("Draft test")
   logging.info(r)
   logging.info("End of randomize the seed by governor")
   # print("Draft test: ", r)
   
   r = []
   if blue_ball is True:
      # randomize numbers by using randint() function
      r = get_random(power55)
   else:
      ts = MEGA45
      if power55 is True:
         ts = POWER55
      r = get_random_sample(power55, ts)
   #dbp(r)
      
   if sort == True:
      if len(r) == JACKPOT_SIX:
         rs = quicksort(r)
      else:
         # Power55's jackpot 2 processing
         # Only quick sort first six elements
         rs = quicksort(r[:6])
         #dbp(rs)
         rs.append(r[6])
   r = rs
   #dbp(r)
   return r
#--------------------------------------------------------------------------
def process_jacklist(power55, fn):
   """Save to global list for later actions"""

   logger = logging.getLogger(__name__)
   assert fn is not None
   tmp = []
   if os.path.isfile(fn) and os.path.getsize(fn) == 0:
      logging.error("ERROR: process_jacklist() fn input failed!")
      return None
   try:
      # Open a file
      jackFile = open(fn, "r")
      #dbp(fn)
   except IOError as inst:
      print("error:", '%s: %s \n' % (fn, inst.strerror))
      logging.error(inst.strerror)
   else:
      for line in jackFile:
         if line.startswith('#'):
            continue
         #
         # Processing current line and save to global numcount variable
         #
         tmp = process(power55, line)
         # End of file will return None
         #
         #dbp(tmp)
         if tmp is not None:
             if power55 is True:
                pnumcount = tmp
             else:
                numcount = tmp
   finally:
      # Close opened file
      jackFile.close()
      
   del jackFile
   #dbp(tmp)
   
   t="process_jacklist():numcount"
   if power55 is True:
      t="process_jacklist():pnumcount"

   logging.info(t)
   logging.info(tmp)
   return tmp
#--------------------------------------------------------------------------
def show_top_pot(power55, t1, t2, t3, t4, p1, p2, p3, p4):
   """Show the final results"""
   
   t="MEGA45: "
   if power55 is True:
      t="POWER55: "
      
   print(t)
   #print("Top1: ", t1)
   #print("Top2: ", t2)
   #print("Top3: ", t3)
   #print("Top4: ", t4)
   print('=' * JACKPOT_SIX * len(t1))
   #print("Pot1: ", p1)
   #print("Pot2: ", p2)
   #print("Pot3: ", p3)
   #print("Pot4: ", p4)
   return None
#--------------------------------------------------------------------------
def write_top_pot_to_ticket(fn, t1, t2, t3, t4, p1, p2, p3, p4, tp):
   """Write to ticket file for reference offline later"""

   write_file(fn, "Top1:", t1)
   write_file(fn, "Top2:", t2)
   write_file(fn, "Top3:", t3)
   write_file(fn, "Top4:", t4)
   write_file(fn, "Pot1:", p1)
   write_file(fn, "Pot2:", p2)
   write_file(fn, "Pot3:", p3)
   write_file(fn, "Pot4:", p4)

   write_file(fn, "Potop:", tp)
   
   return None

#--------------------------------------------------------------------------
def join_list(l, delimiter):
   ll = iter(l)
   newlist = str(next(ll))
   stop = 0
   for i in ll:
      newlist += str(" ") + str(i)
      if len(l) > JACKPOT_SIX:
         stop += 1
         if stop == JACKPOT_SIX - 1:
            newlist += str(delimiter) + str(next(ll))
            
   return newlist
   
#--------------------------------------------------------------------------
def randomize_new_jack_from_list(power55, fn, tplist):
   """Generate another new jack from combined top, pot list"""
   logger = logging.getLogger(__name__)
   #print('=' * JACKPOT_SIX * len(tplist))
   ptoptmp = []
   stop = 0
   while stop < JACKPOT_SIX:
      n = random.sample(tplist, 1)
      j = int(n[0])
      if j not in ptoptmp:
         stop += 1
         ptoptmp.append(j)
   
   ptoplist = quicksort(ptoptmp)
   #dbp(ptoplist)

   # Power55 jackpot2 handling
   if power55 is True:
      stop = 0
      while stop == 0:
         n = random.sample(tplist, 1)
         j = int(n[0])
         if j not in ptoplist:
            ptoplist.append(j)
            stop = 1
            
   #dbp(ptoplist)
   ptoplistFinal = []
   strnum = None
   for num in ptoplist:
      if num < 10:
         strnum = '0' + str(num)
      else:
         strnum = str(num)
      ptoplistFinal.append(strnum)

   t="Next mega45 potop:\t"
   if power55 is True:
      t="Next power55 potop:\t"

   print(t, end='')
   print(join_list(ptoplistFinal, "|"))

   write_file(fn, t, ptoplistFinal)
   logging.info(ptoplistFinal)
   del strnum
   del ptoptmp
   del ptoplist
   del ptoplistFinal
   return None
#--------------------------------------------------------------------------
def random_main(power55, fn):
   """Main function for random generator"""
   logger = logging.getLogger(__name__)
   randomlist = get_random_main(power55)
   #dbp(randomlist)
   if power55 is True:
      print("Next power55 jackpot:\t", end='')
      write_file(fn, "Next power55 jackpot:\t", randomlist)
   else:
      #print("Next jackpot: ", randomlist, sep='\t')
      print("Next mega45 jackpot:\t", end='')
      write_file(fn, "Next jackpot:\t", randomlist)
      #write_file(fn, '=' * JACKPOT_SIX * len(randomlist), "")

   print(join_list(randomlist, "|"))
   logging.info(randomlist)
   return randomlist
#--------------------------------------------------------------------------
def show_random_list(power55, fn):
   """Main function for random list generator"""
   logger = logging.getLogger(__name__)

   if power55 is True:
       logging.info("Random power55 list")
   else:
       logging.info("Random mega45 list")
   r = random_main(power55, fn)
   logging.info(r)
   return None
#--------------------------------------------------------------------------
def show_random_6line_list(power55, fn, fticket):
   """Main function for random 6-line generator"""
   logger = logging.getLogger(__name__)

   logging.info("Random 6-line list")
   bottom = show_six_lines("bottom", fn)
   #print("Bottom: ", bottom)
   rs = []
   while not rs:
      rs = get_random_sample(power55, bottom)
   #print("rs=", rs)
   if len(rs) == JACKPOT_SIX:
      r = quicksort(rs)
   else:
      # Power55's jackpot 2 processing
      # Only quick sort first six elements
      r = quicksort(rs[:6])
      #print("r=", r)
      r.append(rs[6])   
   #dbp(r)
   if python2 is True:
      dprint("Python2 ")
   else:
      dprint("Python3 ")
   if power55 is True:
       logging.info("Random power55 6-line bottom:")
       print("power55 6-line bottom:\t", end='')
   else:
       logging.info("Random mega45 6-line bottom")
       print("mega45 6-line bottom:\t", end='')

   print(join_list(r, "|"))
   write_file(fticket, "Next 6-line:\t", r)
   write_file(fticket, '=' * JACKPOT_SIX * len(r), "")
   logging.info(r)
   del r

   return None
#--------------------------------------------------------------------------
def get_number_of_line(result_file):
   """Get total line from file"""

   uncount = 0
   with open(result_file) as f:
      #lines = len(f.readlines())
      for ll, l in enumerate(f, start=1):
         pass
      for line in f:
         if line.startswith('#'):
            uncount += 1
            continue

   return ll - uncount
#--------------------------------------------------------------------------
def show_six_lines(where, result_file):
   """choose 6 lines from result's top or bottom"""

   sixlines_list = []
   top = False
   total_lines = get_number_of_line(result_file)
   #dbp(total_lines)
   if total_lines < 1:
      raise TypeError("First line is line 1")
   if where == "top":
      top = True

   if total_lines <= JACKPOT_SIX:
      with open(result_file) as f:
         for line in f:
            if line.startswith('#') or len(line) < JACKPOT_LEN - 1:
               continue
            dprint(line)
            #sixlines_list.append(line)
            sixlines_list += convert_line_to_number(line)
         #dbp("sixlines_list)
         return sixlines_list

   # Top
   current_line_count = 0
   if top is True:
      with open(result_file) as f:
         # first line always is line 0
         for line in f:
            if line.startswith('#') or len(line) < JACKPOT_LEN - 1:
               continue
            print(line)
            #sixlines_list.append(line)
            sixlines_list += convert_line_to_number(line)
            current_line_count += 1
            if current_line_count >= JACKPOT_SIX:
               #dbp("sixlines_list)
               return sixlines_list

   # Bottom
   with open(result_file) as f:
      lines = f.readlines()
      ofs = total_lines - JACKPOT_SIX
      while ofs < total_lines:
         x = lines[ofs]
         dprint(x)
         sixlines_list += convert_line_to_number(x)
         ofs += 1
      #dbp("sixlines_list)
      return sixlines_list         
#--------------------------------------------------------------------------
def power55_check_result(power_result_file):
    """check power55 result file exists or not, then create"""

    if os.path.isdir(power_result_file):
       print("error:", '%s: file not found \n' % power_result_file)
       file(power_result_file, 'w').close()
    return True
#--------------------------------------------------------------------------
def main():
   """Main function"""

   print("\nWelcome to vJack cheatsheet!\n")
   dt = datetime.datetime.now()
   timenow = dt.strftime("%Y%m%d-%H%M%S")

   logging.basicConfig(
      filename='debugJack-' + timenow + '.txt',
      #filename='debugJack.txt',
      # filename='inJackpot-debug.txt',
      level=logging.DEBUG,    #  minimum level capture in the file
      # Python Enhancement Proposal #8 violation
      # http://www.python.org/dev/peps/pep-0008/
      # Lines should be 79 characters in length or less.
      format='[%(asctime)s]:[%(filename)s:%(funcName)s]:%(lineno)d %(levelname)s:%(message)s',
      datefmt='%d/%m/%Y %I:%M:%S %p')
   logger = logging.getLogger(__name__)

   logging.info('Started! Welcome to Jackpot cheatsheet!')

   global power_only
   # Full name of the weekday
   today = dt.strftime('%A')
   # Current hour from 01 to 23
   current_time = dt.strftime('%H')
   #print('day name:', (today, type(today)))
   power_only = 0
   if today == "Tuesday" or today == "Thursday" or today == "Saturday":
       if int(current_time) < 18:
           power_only = 1
   else:
       if int(current_time) >= 18:
           power_only = 1
   dbp(power_only)

   r = sys.version_info
   logging.info(r)
   r = sys.version
   r = 'python.' + r
   logging.info(r)
   is_python2()

   # print("arg: ', len(sys.argv))
   if len(sys.argv) != 1:
      usage()
      sys.exit(0)

   # result input file
   resultfile = "./mega-result.txt"
   if os.path.isdir(resultfile):
      print("error:", '%s: file not found \n' % resultfile)
      logging.critical('mega-result.txt not found!')
      sys.exit(0)

   r = mega45_check_result(resultfile)
   if r is False:
      print("error:", '%s file problem\n' % resultfile)
      logging.critical('mega45_check_result() failed!')
      sys.exit(0)

   # power55 result input file
   presultfile = "./power-result.txt"
   power55_check_result(presultfile)
   # TODO: 
   # check and update power result file

   global numcount
   global pnumcount
   global toplist
   global potlist
   pnumcount = [0] * POWERJACK_MAX
   #
   # Process result file and save to global for later use
   #
   tmpcount  = process_jacklist(False, resultfile)
   if tmpcount is not None:
       numcount  = tmpcount
   tmpcount = process_jacklist(True,  presultfile)
   if tmpcount is not None:
       pnumcount = tmpcount
   #dbp(numcount)
   #dbp(pnumcount)
   logging.info("Mega45 numcount")
   logging.info(numcount)
   logging.info("Power55 numcount")
   logging.info(pnumcount)

   #
   # Save to text file for reference offline
   #
   ticketFile = "./ticket45-final.txt"
   r = datetime.datetime.now()
   write_file(ticketFile, "\nRunning in", r)
   pticketFile = "./ticket55-final.txt"
   r = datetime.datetime.now()
   write_file(pticketFile, "\nRunning in", r)


   # Big list to collect all the top, pot numbers
   # We have an option to pick up 6-number `potop`
   global TopPotList
   global pTopPotList
   global savenewtop
   global savenewpot
   global psavenewtop
   global psavenewpot

   # Top1 and Pot1 main handler
   top1list = []
   ptop1list = []
   savenumpot1 = copy.deepcopy(numcount)
   logging.debug(savenumpot1)
   pot1list = []
   ppot1list = []
   dprint(numcount)
   logging.info("Getting Mega45 Top1 and Pot1")
   t, savenewtop, savenewpot = get_potop(False, numcount, savenumpot1, ticketFile)
   numcount = t
   numcount = savenewtop
   #dbp(numcount)
   #dbp(savenewpot)
   logging.info("Re-update Mega45 numcount for next top2")
   logging.info(numcount)
   top1list = toplist
   pot1list = potlist
   dprint(pnumcount)
   logging.info("Getting Power55 Top1 and Pot1")
   t, psavenewtop, psavenewpot = get_potop(True, pnumcount, pnumcount, pticketFile)
   # pnumcount = t
   pnumcount = psavenewtop
   #dbp(pnumcount)
   #dbp(psavenewpot)
   logging.info("Re-update Power55 pnumcount for next top2")
   logging.info(pnumcount)
   ptop1list = toplist
   ppot1list = potlist

   # Top2 and Pot2 main handler
   top2list = []
   ptop2list = []
   # savenumpot2 = savenumpot1
   savenumpot2 = savenewpot
   psavenumpot2 = psavenewpot
   logging.debug(savenumpot2)
   pot2list = []
   ppot2list = []
   dprint(numcount)
   logging.info("Getting Mega45 Top2 and Pot2")
   t, savenewtop, savenewpot = get_potop(False, numcount, savenumpot2, ticketFile)
   # numcount = t
   numcount = savenewtop
   #dbp(numcount)
   #dbp(numcount)
   #dbp(savenewpot)
   logging.info("Re-update Mega45 numcount for next top3")
   logging.info(numcount)
   top2list = toplist
   pot2list = potlist
   #dbp(pot2list)
   #dbp(pnumcount)
   logging.info("Getting Power55 Top2 and Pot2")
   t, psavenewtop, psavenewpot = get_potop(True, pnumcount, psavenumpot2, pticketFile)
   # pnumcount = t
   pnumcount = psavenewtop
   dprint(pnumcount)
   #dbp(pnumcount)
   #dbp(psavenewpot)
   logging.info("Re-update Power55 pnumcount for next top3")
   logging.info(pnumcount)
   ptop2list = toplist
   ppot2list = potlist

   # Top3 and Pot3 main handler
   top3list = []
   ptop3list = []
   savenumpot3 = savenewpot
   psavenumpot3 = psavenewpot
   logging.debug(savenumpot3)
   pot3list = []
   ppot3list = []
   dprint(numcount)
   logging.info("Getting Mega45 Top3 and Pot3")
   t, savenewtop, savenewpot = get_potop(False, numcount, savenumpot3, ticketFile)
   # numcount = t
   numcount = savenewtop
   # print("numcount = ", numcount)
   # print("potcount = ", savenewpot)
   dprint(numcount)
   logging.info("Re-update Mega45 numcount for next top4")
   logging.info(numcount)
   top3list = toplist
   pot3list = potlist
   # print("pot3list = ", pot3list)
   # print(pnumcount)
   logging.info("Getting Power55 Top3 and Pot3")
   t, psavenewtop, psavenewpot = get_potop(True, pnumcount, psavenumpot3, pticketFile)
   # pnumcount = t
   pnumcount = psavenewtop
   dprint(pnumcount)
   logging.info("Re-update Power55 pnumcount for next top4")
   logging.info(pnumcount)
   # print("pnumcount = ", pnumcount)
   # print("ppotcount = ", psavenewpot)
   ptop3list = toplist
   ppot3list = potlist

   # Top4 and Pot4 main handler
   top4list = []
   ptop4list = []
   savenumpot4 = savenewpot
   psavenumpot4 = psavenewpot
   logging.debug(savenumpot4)
   pot4list = []
   ppot4list = []
   #dbp(numcount)
   logging.info("Getting Mega45 Top4 and Pot4")
   t, savenewtop, savenewpot = get_potop(False, numcount, savenumpot4, ticketFile)
   numcount = savenewtop
   #dbp(numcount)
   #dbp(savenewpot)
   #dbp(numcount)
   logging.info("Re-update last Mega45 numcount")
   logging.info(numcount)
   top4list = toplist
   pot4list = potlist
   #dbp(pot4list)
   #dbp(pnumcount)
   logging.info("Getting Power55 Top4 and Pot4")
   t, psavenewtop, psavenewpot = get_potop(True, pnumcount, psavenumpot4, pticketFile)
   pnumcount = psavenewtop
   dprint(pnumcount)
   logging.info("Re-update last Power55 pnumcount")
   logging.info(pnumcount)
   #dbp(pnumcount)
   #dbp(psavenewpot)
   ptop4list = toplist
   ppot4list = potlist

   #
   # Preparation
   # 
   preparation(False)

   # Summary all statistics
   show_top_pot(False, top1list, top2list, top3list, top4list,
           pot1list, pot2list, pot3list, pot4list)
   randomize_new_jack_from_list(False, ticketFile, TopPotList)
   show_random_list(False, ticketFile)
   show_random_6line_list(False, resultfile, ticketFile)

   # Save to log
   logging.info("Top numbers")
   logging.info(top1list)
   logging.info(top2list)
   logging.info(top3list)
   logging.info(top4list)
   logging.info("Pot numbers")
   logging.info(pot1list)
   logging.info(pot2list)
   logging.info(pot3list)
   logging.info(pot4list)
   logging.info("Potop numbers")
   logging.info(TopPotList)
   logging.info(pTopPotList)
   # Save to ticket file
   write_top_pot_to_ticket(ticketFile, top1list, top2list, top3list, top4list,
           pot1list, pot2list, pot3list, pot4list, TopPotList)

   print("\n")
   #print('=' * JACKPOT_SIX * len(ppot3list))
   show_top_pot(True, ptop1list, ptop2list, ptop3list, ptop4list,
          ppot1list, ppot2list, ppot3list, ppot4list)
   randomize_new_jack_from_list(True, pticketFile, pTopPotList)
   show_random_list(True, pticketFile)
   show_random_6line_list(True, presultfile, pticketFile)
   write_top_pot_to_ticket(pticketFile, ptop1list, ptop2list, ptop3list,
           ptop4list,
           ppot1list, ppot2list, ppot3list, ppot4list, pTopPotList)

   del TopPotList
   del pTopPotList

   print("\nDone!\n")
   logging.info('Finished!')
   logging.shutdown()
   #
   # Cleanup
   #
   del ticketFile

   sys.exit(0)

if __name__ == '__main__':
   main()
