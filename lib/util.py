import math;
from datetime import datetime, timedelta;
from calendar import timegm;

perSecond = 1
perMinute = perSecond * 60
perHour = perMinute * 60
perHalfDay = perHour * 12
perDay = perHalfDay * 2
perWeek = perDay * 7
perMonth = perWeek * 4
perQuarter = perMonth * 4
perYear = perDay * 365

def dt_min(period, val):
    seconds = math.floor(timegm(val.utctimetuple()) / period) * period

    # Trying not to piss off the leap year gods...
    #seconds += int((perDay * seconds) / (perYear * 4))

    return datetime.utcfromtimestamp(seconds)
            #int(timegm(
            #        val.utctimetuple()) / period) * period)

def seconds_between(a, b):
    return abs((b - a).total_seconds())

def ci_rate(p, d, t):
    a = p + d
    if(p == 0 or t == 0):
        return 0.0
    return math.log(a / p) / t

def pert(p, r, t):
    return p * (math.e ** (r * t))
