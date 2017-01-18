import urllib
import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta

name = 'Coinbase'
rateLimit = 10000
rateDelta = timedelta(hours=1)

def mkUri(currencyPair):
    return "https://api.coinbase.com/v2/prices/" + currencyPair + "/spot"

def getPrice(currencyPair = "BTC-USD", date = None):
    query = {}
    if(date):
        query['date'] = date.strftime("%Y-%m-%d");
    q = urllib.parse.urlencode(query)

    req = urllib.request.Request(mkUri(currencyPair) + "?" + q)
    req.headers["CB-VERSION"] = "2015-04-08"
    ret = urllib.request.urlopen(req)

    val = json.loads(ret.readall().decode('utf-8'))

    return (datetime.now(), val['data']['amount'])

ops = [
        {
            "name": "PriceUSDBTC",
            "fn": lambda : getCurrentPrice('BTC-USD')
        }
    ];
