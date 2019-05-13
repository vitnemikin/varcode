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
        #print data
        return data
    except ValueError:
        return []



def GetMediumStockDay(dtime):
    try:
        i     = STOCK['timestamp'].index(Timestamp(dtime.replace(hour=9,  minute=55)))
        i_max = STOCK['timestamp'].index(Timestamp(dtime.replace(hour=18, minute=45)))
    except ValueError:
        return []
    
    dat = STOCK['price'][i]
    dat.append(STOCK['volume'][i][0])
    hi = dat[0]
    lo = dat[1]
    op = dat[2]
    
    vl = dat[4]
    
    while i < i_max:
        i += 1
        dat = STOCK['price'][i]
        dat.append(STOCK['volume'][i][0])
        if hi < dat[0]:
            hi = dat[0]
        if lo > dat[1]:
            lo = dat[1]
        vl += dat[4]
    
    cl = dat[3]
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


def Norm(values, base):
    if type(values) != list:
        return (values - base['price']) / base['price']
    result = []
    for price in values[0:-1]:
        result.append((price - base['price']) / base['price'])
    #result.append((values[-1] - base['volume']) / base['volume'])
    result.append((values[-1] + 0.0) / base['volume'])
    return result



extract_days, extract_file = ParseArgs(sys.argv)
if extract_file == '' or extract_file == '-h' or extract_file == '--help':
    Die("Usage: " + sys.argv[0] + " [days] FILE")
    
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



base = {}
extracted = {}




def ProcessExtractedData():
    raw = []
    for val in extracted['d-3']:
        raw.append(val)
    for val in extracted['d-2']:
        raw.append(val)
    for val in extracted['d-1']:
        raw.append(val)
    for val in extracted['9_55']:
        raw.append(val)
    for val in extracted['10_00']:
        raw.append(val)
    for val in extracted['10_05']:
        raw.append(val)
    for val in extracted['10_10']:
        raw.append(val)
    for val in extracted['10_15']:
        raw.append(val)
    for val in extracted['10_20']:
        raw.append(val)
    for val in extracted['10_25']:
        raw.append(val)
    for val in extracted['10_30']:
        raw.append(val)
    for val in extracted['10_35']:
        raw.append(val)
    for val in extracted['10_40']:
        raw.append(val)
    for val in extracted['10_45']:
        raw.append(val)
    for val in extracted['10_50']:
        raw.append(val)
    for val in extracted['10_55']:
        raw.append(val)
    #print len(raw), raw




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
    base['price']  = back_1day[3] + 0.0
    base['volume'] = back_1day[4] + 0.0
    
    extracted['d-3'] = Norm(back_3days[0:5], base)
    extracted['d-2'] = Norm(back_2days[0:5], base)
    extracted['d-1'] = Norm(back_1day[0:5], base)
    extracted['9_55']    = Norm(day_opened[0:5], base)
    extracted['10_00']   = Norm(GetStockAt(dayx.replace(hour=10, minute=00))[0:5], base)
    extracted['10_05']   = Norm(GetStockAt(dayx.replace(hour=10, minute=05))[0:5], base)
    extracted['10_10']   = Norm(GetStockAt(dayx.replace(hour=10, minute=10))[0:5], base)
    extracted['10_15']   = Norm(GetStockAt(dayx.replace(hour=10, minute=15))[0:5], base)
    extracted['10_20']   = Norm(GetStockAt(dayx.replace(hour=10, minute=20))[0:5], base)
    extracted['10_25']   = Norm(GetStockAt(dayx.replace(hour=10, minute=25))[0:5], base)
    extracted['10_30']   = Norm(GetStockAt(dayx.replace(hour=10, minute=30))[0:5], base)
    extracted['10_35']   = Norm(GetStockAt(dayx.replace(hour=10, minute=35))[0:5], base)
    extracted['10_40']   = Norm(GetStockAt(dayx.replace(hour=10, minute=40))[0:5], base)
    extracted['10_45']   = Norm(GetStockAt(dayx.replace(hour=10, minute=45))[0:5], base)
    extracted['10_50']   = Norm(GetStockAt(dayx.replace(hour=10, minute=50))[0:5], base)
    extracted['10_55']   = Norm(GetStockAt(dayx.replace(hour=10, minute=55))[0:5], base)
    extracted['day_sum'] = Norm(GetMediumStockDay(dayx)[0:5], base)
    print str(i+1)+":", StrDt(dayx), ", base price", base['price'], ", base volume", base['volume']
    print json.dumps(extracted)
    
    ProcessExtractedData()
    
    
    print ""
    extracted = {}
    i += 1


print "End."
