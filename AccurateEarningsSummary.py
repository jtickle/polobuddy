#!/usr/bin/env python3

from lib.pololib import *
from lib.util import *
from datetime import date, datetime, timedelta
from time import sleep
import lib.coinbase as coinbase
from pprint import pprint

dayRate = {}
report = {}

def createApi():
    secrets = json.loads(open('secrets').read())
    apikey = str(secrets['apikey'])
    secret = str(secrets['secret'])

    print("Using API key " + apikey, file=sys.stderr)
    return poloniex(apikey, secret)

def getBtcUsd(inDate):
    day = date.fromordinal(inDate.toordinal())

    # If it's cached, return it
    if(day in dayRate):
        return dayRate[day];

    # Snapshot the current time
    currTime = datetime.now()

    # Request the price
    btcusd=float(coinbase.getPrice(date=day)[1])

    # Cache the price
    dayRate[day] = btcusd

    # Debug
    #print("{0}: {1}".format(day, btcusd))

    # Wait so we don't accidentally do more than the limit
    wtime = (coinbase.rateDelta.total_seconds() / coinbase.rateLimit) \
            - (datetime.now()- currTime).total_seconds()
    if(wtime > 0):
        #print("Using Coinbase Responsibly by waiting {0} seconnds..."
        #        .format(wtime));
        sleep(wtime)

    # Return the price
    return btcusd
        
api = createApi()
history = api.getLendingHistory()
active = api.getActiveLoans()

for loan in history:

    # Discard unprofitable loans
    if(loan['interest'] < 0.00000010):
        continue;

    if(loan['fee'] > -0.00000001):
        continue;

    if(loan['currency'] not in report):
        report[loan['currency']] = {}

    report[loan['currency']][loan['close']] = {
            "id":          loan['id'],
            "duration":    loan['duration'],
            "rate":        loan['rate'],
            "amount":      loan['amount'],
            "interest":    loan['interest'],
            "fee":         loan['fee'],
            "earned":      loan['earned'],
            "return":      ci_rate(loan['amount'], loan['earned'],
                loan['duration']),
            "active":      False}

for loan in active['provided']:

    if(loan['currency'] not in report):
        report[loan['currency']] = {}

    numDays = (datetime.utcnow() - loan['date']).total_seconds() / 86400

    interest = pert(loan['amount'],
                    loan['rate'],
                    numDays) - loan['amount']
    fee = -(loan['fees'] * 0.15)
    earned = interest + fee
    rate = ci_rate(loan['amount'], earned, numDays)

    close = loan['date'] + timedelta(
            seconds=int(loan['duration'] * 24 * 60 * 60))

    report[loan['currency']][close] = {
            "id":       loan['id'],
            "duration": numDays,
            "rate":     loan['rate'],
            "amount":   loan['amount'],
            "interest": interest,
            "fee":      fee,
            "earned":   earned,
            "return":   rate,
            "active":   True}

print('"Close",'+
#      '"Id",'+
      '"Duration",'+
      '"Rate",'+
      '"Principal",'+
      '"Interest",'+
      '"Fee",'+
      '"Earned",'+
      '"Return Rate",'+
      '"Fee %",'+
#      '"InterestSum",'+
#      '"FeeSum",'+
      '"EarnedSum",'+
      '"Est. APY",'+
      '"USD Earned",'+
      '"Estimate"')

interest = 0
fee = 0
earned = 0

skipped = 0

pprint(report)

for close in sorted(report['BTC'].keys()):
    d = dict(report['BTC'][close])
    d['close'] = close
    d['feepct'] = -d['fee'] / d['interest']

    interest += d['interest']
    fee      += d['fee']
    earned   += d['earned']
    feepct    = -fee / interest
    
    d['interestsum'] = interest
    d['feesum']      = fee
    d['earnedsum']   = earned
    d['feepctsum']   = feepct

    req = close
    if(close > datetime.now()):
        close = datetime.now()
    d['usdsum']      = d['earnedsum'] * getBtcUsd(close)

    if(d['active']):
        d['active'] = "*"
    else:
        d['active'] = ""

    if(d['duration'] == 0):
        d['apy'] = 0
    else:
        d['apy'] = d['return'] * 36500

#    if(d['earned'] < 0.00000010 or d['duration'] == 0):
#        skipped += 1
#        continue

    if(skipped):
        #print("skipped {0} junk".format(skipped))
        skipped = 0

    print(("{close},"+
#          "{id:10},"+
          "{duration:11.8f},"+
          "{rate:11.8f},"+
          "{amount:11.8f},"+
          "{interest:11.8f},"+
          "{fee:11.8f},"+
          "{earned:11.8f},"+
          "{return:11.8f},"+
          "{feepct:11.8f},"+
#          "{interestsum:10.8f},"+
#          "{feesum:11.8f},"+
          "{earnedsum:11.8f},"+
          "{apy:5.2f}"+
          "{usdsum:5.2f}"+
          "{active:>6}").format(**d))
