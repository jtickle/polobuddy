#!/usr/bin/env python3

from lib.pololib import *
from lib.util import *
import argparse;
import plotly;

def createApi():
    secrets = json.loads(open('secrets').read())
    apikey = str(secrets['apikey'])
    secret = str(secrets['secret'])

    print("Using API key " + apikey, file=sys.stderr)
    return poloniex(apikey, secret)

def addActiveLoansToHistory(history, active):
    for loan in active:
        interest = pert(loan['amount'], loan['rate'], loan['duration']) - loan['amount']
        history.append({
            'open': loan['date'],
            'currency': loan['currency'],
            'amount': loan['amount'],
            'fee': -loan['fees'],
            # The following are estimates
            'interest': interest,
            'earned': interest - loan['fees']})

def addLoanToSummary(summary, intervalSecs, now, loan):

    # Set the Open time to the real open time
    dt_open = loan['open']

    # If there is no close time, make it close today for
    # the math but not show that it has been closed to be accurate
    if('close' in loan):
        dt_close = loan['close']
        totalSecs = seconds_between(dt_open, dt_close)
    else:
        dt_close = None
        totalSecs = seconds_between(dt_open, now)

    if(totalSecs == 0):
        return

    # We divide up the loan into intervalSecs chunks of seconds
    p_start = dt_min(intervalSecs, dt_open)
    p_end = 0
    while(True):

        # Define the end of the next interval
        p_end = p_start + timedelta(0, intervalSecs)

        # Set default values
        openings = 0
        closings = 0
        seconds = intervalSecs

        # Handle partial first interval
        if(dt_open > p_start):
            openings = 1
            seconds -= seconds_between(p_start, dt_open)

        # Handle partial last interval
        if(dt_close is not None and dt_close < p_end):
            closings = 1
            seconds -= seconds_between(dt_close, p_end)

        # If interval hasn't been visited yet, create defaults
        if(p_start not in summary):
            n = {}
            n['count'] = 0
            n['seconds'] = 0
            n['openings'] = 0
            n['closings'] = 0
            n['principal'] = 0.0
            n['interest'] = 0.0
            n['fee'] = 0.0
            n['earned'] = 0.0
            n['rate'] = 0.0
            n['return'] = 0.0
            summary[p_start] = n

        # Work the values into the interval summary
        n = summary[p_start]
        n['count']     += 1
        n['seconds']   += int(seconds)
        n['openings']  += openings
        n['closings']  += closings
        n['principal'] += (loan['amount']   * seconds) / intervalSecs
        n['interest']  += (loan['interest'] * seconds) / totalSecs
        n['fee']       += (loan['fee']      * seconds) / totalSecs
        n['earned']    += (loan['earned']   * seconds) / totalSecs

        # If this is the last interval, break
        if(now < p_end or (dt_close and dt_close < p_end)):
            break

        # Define the start of the next interval
        p_start = p_end


def makeAggregates(cursum, intervalSecs):
    principalsum = 0
    interestsum = 0
    feesum = 0
    earnedsum = 0
    for interval, s in sorted(cursum.items()):

        s["rate"]   = ci_rate(s["principal"], s["interest"],
                intervalSecs / 86400)
        s["return"] = ci_rate(s["principal"], s["interest"] + s["fee"],
                intervalSecs / 86400)

        s["apy"] = (s["return"] * 365)

        principalsum += s["principal"]
        interestsum += s["interest"]
        feesum += s["fee"]
        earnedsum += s["earned"]
        s["principalsum"] = principalsum
        s["interestsum"] = interestsum
        s["feesum"] = feesum
        s["earnedsum"] = earnedsum

def lendingHistoryReport(api, intervalSecs):
    # Get lending history
    lendingHistory = api.getLendingHistory()
    
    # Add active loans to lending history
    addActiveLoansToHistory(lendingHistory,
            api.getActiveLoans()['provided'])

    summary = {}

    # It may take time to run the report, so let's save
    # what now is and use it consistently.
    now = datetime.now()

    for loan in lendingHistory:

        # Handle defaults for new currency
        currency = loan['currency']
        if currency not in summary:
            summary[currency] = {}

        # Add the loan to the currency summary
        addLoanToSummary(summary[currency], intervalSecs, now, loan)

    # Perform aggregate operations on the intervals
    for currency, cursum in summary.items():
        makeAggregates(cursum, intervalSecs)

    return {
            "begin": datetime.min,
            "end": now,
            "report": summary}

def summarycsv(summary):
    print('"Currency", "Time Period", "Openings", "Closings", '+
          '"Open Loans", "Principal", "Interest Earned", "Fees Paid", '+
          '"Net Earnings", "Interest Rate", "Return Rate with Fees", '+
          '"Estimated APY", "Total Earnings"')
    for currency, cursum in summary['report'].items():
        for period, persum in sorted(cursum.items()):
            position = dict(persum)
            position['currency'] = currency
            position['period'] = period
            print(("\"{currency}\","+
                   "\"{period}\","+
                   "{openings:3},"+
                   "{closings:3},"+
                   "{count:3},"+
                   "{principal:12.8f},"+
                   "{interest:12.8f},"+
                   "{fee:12.8f},"+
                   "{earned:12.8f},"+
                   "{rate:12.8f},"+
                   "{return:12.8f},"+
                   "{apy:12.8f},"+
                   "{earnedsum:12.8f}")
                       .format(**position))

parser = argparse.ArgumentParser(
    description='Generate a lending history report for Poloniex')
parser.add_argument('-M', '--per-minute',
        action='store_const', const=perMinute,
        dest='interval')
parser.add_argument('-H', '--per-hour',
        action='store_const', const=perHour,
        dest='interval')
parser.add_argument('-4', '--per-four-hours',
        action='store_const', const=perHour * 4,
        dest='interval')
parser.add_argument('-12', '--per-half-day',
        action='store_const', const=perHalfDay,
        dest='interval')
parser.add_argument('-d', '--per-day',
        action='store_const', const=perDay,
        dest='interval')
parser.add_argument('-w', '--per-week',
        action='store_const', const=perWeek,
        dest='interval')
parser.add_argument('-m', '--per-month',
        action='store_const', const=perMonth,
        dest='interval')
parser.add_argument('-q', '--per-quarter',
        action='store_const', const=perQuarter,
        dest='interval')
parser.add_argument('-y', '--per-year',
        action='store_const', const=perYear,
        dest='interval')
parser.add_argument('-i', '--interval',
        dest='interval')

parsed = parser.parse_args()

if(parsed.interval):
    interval = int(parser.parse_args().interval)
else:
    interval = perDay

if(interval < perMinute):
    print("Invalid interval " + str(interval) + "; must be a minute or more",
            file = sys.stderr)
    quit(1)

print("Using interval " + str(interval), file=sys.stderr)

api = createApi()
summary = lendingHistoryReport(api, interval)
summarycsv(summary)
