#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import json
from datetime import datetime, timedelta
from pytz import timezone

TZ    = timezone('UTC')
EP    = datetime(1970, 1, 1, tzinfo=TZ)   #epoch
STOCK = {}
stock_begin = EP
stock_end = EP
d_1day = timedelta(days=1)


def Die(msg):
    print msg
    exit(-1)


def ParseArgs(argv):
    if len(argv) <= 1:
        return 0, ''
    if len(argv) == 2:
        return -1, argv[1]
    if len(argv) > 2:
        if not argv[1].isdigit():
            return 0, ''
        return int(argv[1]), argv[2]


def FileExists(fname):
	try:
		test_file = open(fname,'r')
	except IOError:
		return False
	test_file.close()
	return True


def Timestamp(dtime):
    return (dtime - EP).total_seconds()

def StrDt(dtime):
    return dtime.strftime('%d %h %Y %H:%M')


def FirstAndLastTime(ts_array):
    return datetime.fromtimestamp(ts_array[0], TZ), datetime.fromtimestamp(ts_array[-1], TZ)


def GetStockAt(dtime):
    try:
        data = STOCK['price'][STOCK['timestamp'].index(Timestamp(dtime))]
        data.append(STOCK['volume'][STOCK['timestamp'].index(Timestamp(dtime))][0])
        print data
        return data
    except ValueError:
        return []



def GetMediumStockDay(dtime):
    try:
        i     = STOCK['timestamp'].index(Timestamp(dtime.replace(hour=9,  minute=55)))
        i_max = STOCK['timestamp'].index(Timestamp(dtime.replace(hour=18, minute=45)))
    except ValueError:
        return []
    
    data = STOCK['price'][i]
    data.append(STOCK['volume'][i][0])
    hi = data[0]
    lo = data[1]
    op = data[2]
    
    vl = data[4]
    
    while i < i_max:
        i += 1
        data = STOCK['price'][i]
        data.append(STOCK['volume'][i][0])
        if hi < data[0]:
            hi = data[0]
        if lo > data[1]:
            lo = data[1]
        vl += data[4]
    
    cl = data[3]
    return [hi, lo, op, cl, vl]



def GetMediumStockDaysBack(current_day, back_days):
    day = current_day - d_1day
    i = 1
    while i <= back_days:
        if day < stock_begin:
            break
        if len(GetStockAt(day)):
            if i == back_days:
                return GetMediumStockDay(day)
            else:
                i += 1
        day -= d_1day
    return []



extract_days, extract_file = ParseArgs(sys.argv)
if not FileExists(extract_file):
    Die("ERROR: file " + extract_file + " not available")

try:
    STOCK = json.load(open(extract_file,'r'))
except ValueError:
    Die("ERROR: bad data in " + extract_file)

stock_begin, stock_end = FirstAndLastTime(STOCK['timestamp'])

if not stock_end > stock_begin:
    Die("ERROR: check time interval in stock data")

if extract_days == -1:
    extract_days = len(STOCK['timestamp'])



print "Ticker:", STOCK['ticker']
print "Begin:", StrDt(stock_begin), ", End:", StrDt(stock_end)
print "Extract", extract_days, "days"



extracted = {}
dayx = stock_begin
i = 0

while i < extract_days:
    dayx += d_1day
    if dayx >= stock_end:
        break
    #print str(i+1)+":", StrDt(dayx)
    back_3days = GetMediumStockDaysBack(dayx, 3)
    if not len(back_3days):
        continue
    back_2days = GetMediumStockDaysBack(dayx, 2)
    if not len(back_2days):
        continue
    back_1day  = GetMediumStockDaysBack(dayx, 1)
    if not len(back_1day):
        continue
    day_opened = GetStockAt(dayx.replace(hour=9,  minute=55))
    if not len(day_opened):
        continue
    
    extracted['d-3'] = back_3days
    extracted['d-2'] = back_2days
    extracted['d-1'] = back_1day
    extracted['9_55']    = day_opened
    extracted['10_00']   = GetStockAt(dayx.replace(hour=10, minute=00))
    extracted['10_05']   = GetStockAt(dayx.replace(hour=10, minute=05))
    extracted['10_10']   = GetStockAt(dayx.replace(hour=10, minute=10))
    extracted['10_15']   = GetStockAt(dayx.replace(hour=10, minute=15))
    extracted['10_20']   = GetStockAt(dayx.replace(hour=10, minute=20))
    extracted['10_25']   = GetStockAt(dayx.replace(hour=10, minute=25))
    extracted['10_30']   = GetStockAt(dayx.replace(hour=10, minute=30))
    extracted['10_35']   = GetStockAt(dayx.replace(hour=10, minute=35))
    extracted['10_40']   = GetStockAt(dayx.replace(hour=10, minute=40))
    extracted['10_45']   = GetStockAt(dayx.replace(hour=10, minute=45))
    extracted['10_50']   = GetStockAt(dayx.replace(hour=10, minute=50))
    extracted['10_55']   = GetStockAt(dayx.replace(hour=10, minute=55))
    extracted['day_sum'] = GetMediumStockDay(dayx)
    print str(i+1)+":", StrDt(dayx)
    print json.dumps(extracted)
    print ""
    extracted = {}
    i += 1


print "End."
