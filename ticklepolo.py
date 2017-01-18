#!/usr/bin/env python3
from lib import poloapi, pololib
import math
import json
import time
import sys
from datetime import datetime, timedelta
from pprint import pprint

def create():
    secrets = json.loads(open('secrets').read())
    apikey = str(secrets['apikey'])
    secret = str(secrets['secret'])

    print("Using API key " + apikey, file=sys.stderr)
    return pololib.poloniex(apikey, secret)

def calculateRateFromPDT(p, d, t):
    a = p + d
    if(p == 0 or t == 0):
        return 0.0
    return math.log(a / p) / t

def calculateRate(h):
    p = h['amount']
    d = h['interest']
    t = h['duration']
    return calculateRateFromPDT(p, d, t);

def calculateReturn(h):
    p = h['amount']
    d = p + h['earned']
    t = h['duration']
    return calculateRateFromPDT(p, d, t);

def prettyLending(api):
    history = api.returnLendingHistory()
    if("error" in history):
        print("error", file=sys.stderr)
        quit()
    interest = float(0)
    earned = float(0)
    fees = float(0)

    head = "       id               close    duration      amount       rate     interest         fee      earned"
    count = 0
    for h in history:
        count += 1
        if (count % 10 == 0):
            print(head)
        h = convertHistory(h)
        interest += h['interest']
        earned   += h['earned']
        fees     += h['fee']
        h['calcRate'] = calculateRate(h)
        h['return'] = calculateReturn(h)
        print("{id:9} {close} {duration: 10.8f} {amount: 10.8f} {rate: 10.8f} {interest: 10.8f} {fee: 11.8f} {earned: 10.8f} {calcRate: 10.8f} {return: 10.8f}".format(**h))

    print("Total Interest: " + str(interest))
    print("Total Fees: " + str(fees))
    print("Total Earnings (given): " + str(earned))
    print("Total Earnings (calculate): " + str(interest + fees))

def overHistory(api):
    history = api.returnLendingHistory()

    for v in history:
        yield convertHistory(v)

def times(api):
    history = api.returnLendingHistory()

    for v in history:
        h = convertHistory(v)
        print(h['open'], h['close'])

def earned(api):
    history = api.returnLendingHistory()

    for v in history:
        h = convertHistory(v)
        print(h['earned'])

summarycsv(create().summarizeHistory())
#pprint(create().getActiveLoans())
