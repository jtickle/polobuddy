import urllib
import urllib.request
import urllib.parse
import json
import time
from datetime import datetime
import hmac,hashlib

date_time_format = "%Y-%m-%d %H:%M:%S"

def strToDT(s):
    return datetime.strptime(s, date_time_format)

def DTToStr(dt):
    return dt.strftime(date_time_format)

def clean_locals(vals):
    # Make a copy
    ret = dict(vals)
    # Delete "self" which is passed in on every call
    del ret['self']
    for key in vals:
        # Delete empty values
        if vals[key] == None:
            del ret[key]
        # Convert datetimes to unix ts
        if isinstance(vals[key], datetime):
            ret[key] = vals[key].total_seconds()
    return ret

get_uri = 'https://poloniex.com/public'
post_uri = 'https://poloniex.com/tradingApi'

class poloniex:
    def __init__(self, APIKey, Secret):
        self.APIKey = APIKey
        self.Secret = str(Secret).encode('utf-8')

    def api_get(self, command, req={}):
        # Add command to request
        req['command'] = command;
        # Create query string
        query = urllib.parse.urlencode(req);
        # Execute the request
        ret = urllib.request.urlopen(urllib.request.Request(get_uri + "?" + query))
        # Decode JSON and return
        return json.loads(ret.readall().decode('utf-8'))

    def api_post(self, command, req={}):
        # Add command, nonce to request
        req['command'] = command
        req['nonce'] = int(time.time()*1000)
        # Create post data
        post_data = urllib.parse.urlencode(req).encode('utf-8');

        # Sign post data
        sign = hmac.new(
                self.Secret,
                post_data,
                hashlib.sha512).hexdigest()
        headers = {
            'Sign': sign,
            'Key': self.APIKey
        }

        # Execute the request
        ret = urllib.request.urlopen(urllib.request.Request(post_uri, post_data, headers))
        # Decode JSON and return
        return json.loads(ret.readall().decode('utf-8'))

    def returnTicker(self):
        return self.api_get("returnTicker")

    def return24Volume(self):
        return self.api_get("return24Volume")

    def returnOrderBook (self, currencyPair="all", depth=None):
        vals = clean_locals(locals())
        return self.api_get("returnOrderBook", vals)

    def returnMarketTradeHistory (self, currencyPair, start=None, end=None):
        vals = clean_locals(locals())
        return self.api_get("returnTradeHistory", vals)

    def returnChartData (self, currencyPair="all", start=None, end=None,
            period=None):
        vals = clean_locals(locals())
        return self.api_get("returnChartData", vals)

    def returnCurrencies (self):
        return self.api_get("returnCurrencies")

    def returnLoanOrders (self, currency):
        vals = clean_locals(locals())
        return self.api_get("returnLoanOrders")

    # Returns all of your balances.
    # Outputs: 
    # {"BTC":"0.59098578","LTC":"3.31117268", ... }
    def returnBalances(self):
        return self.api_post("returnBalances")

    def returnCompleteBalances(self, account = None):
        vals = clean_locals(locals())
        return self.api_post("returnCompleteBalances", vals)

    def returnDepositAddresses(self):
        return self.api_post("returnDepositAddresses")

    def generateNewAddress(self, currency):
        vals = clean_locals(locals())
        return self.api_post("generateNewAddress", vals)

    def returnDepositsWithdrawals(self, start, end):
        vals = clean_locals(locals())
        return self.api_post("returnDepositsWithdrawals", vals)

    # Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_XCP"
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs: 
    # orderNumber   The order number
    # type          sell or buy
    # rate          Price the order is selling or buying at
    # Amount        Quantity of order
    # total         Total value of order (price * quantity)
    def returnOpenOrders(self,currencyPair = "all"):
        vals = clean_locals(locals())
        return self.api_post('returnOpenOrders',vals)


    # Returns your trade history for a given market, specified by the "currencyPair" POST parameter
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs: 
    # date          Date in the form: "2014-02-19 03:44:59"
    # rate          Price the order is selling or buying at
    # amount        Quantity of order
    # total         Total value of order (price * quantity)
    # type          sell or buy
    def returnTradeHistory(self,currencyPair = "all"):
        vals = clean_locals(locals())
        return self.api_post('returnTradeHistory',vals)

    def returnOrderTrades (self, orderNumber):
        vals = clean_locals(locals())
        return self.api_post("returnOrderTrades", vals)

    # Places a buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is buying at
    # amount        Amount of coins to buy
    # Outputs: 
    # orderNumber   The order number
    def buy(self,currencyPair,rate,amount,fillOrKill=None,immediateOrCancel=None,postOnly=None):
        vals = clean_locals(locals())
        return self.api_post('buy',vals)

    # Places a sell order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is selling at
    # amount        Amount of coins to sell
    # Outputs: 
    # orderNumber   The order number
    def sell(self,currencyPair,rate,amount,fillOrKill=None,immediateOrCancel=None,postOnly=None):
        vals = clean_locals(locals())
        return self.api_post('sell',vals)

    # Cancels an order you have placed in a given market. Required POST parameters are "currencyPair" and "orderNumber".
    # Inputs:
    # currencyPair  The curreny pair
    # orderNumber   The order number to cancel
    # Outputs: 
    # succes        1 or 0
    def cancelOrder(self,orderNumber):
        vals = clean_locals(locals())
        return self.api_post("cancelOrder", vals)

    # Immediately places a withdrawal for a given currency, with no email confirmation. In order to use this method, the withdrawal privilege must be enabled for your API key. Required POST parameters are "currency", "amount", and "address". Sample output: {"response":"Withdrew 2398 NXT."} 
    # Inputs:
    # currency      The currency to withdraw
    # amount        The amount of this coin to withdraw
    # address       The withdrawal address
    # Outputs: 
    # response      Text containing message about the withdrawal
    def withdraw(self, currency, amount, address, paymentId=None):
        vals = clean_locals(locals())
        return self.api_post('withdraw',vals)

    def returnFeeInfo(self):
        return self.api_post("returnFeeInfo")

    def returnAvailableAccountBalances(self, account=None):
        vals = clean_locals(locals())
        return self.api_post("returnAvailableAccountBalances", vals)

    def returnTradableBalances(self):
        return self.api_post("returnTradableBalances")

    def transferBalance(self, currency, amount, fromAccount, toAccount):
        vals = clean_locals(locals())
        return self.api_post("transferBalance", vals)

    def returnMarginAccountSummary(self):
        return self.api_post("returnMarginAccountSummary", vals)

    def marginBuy(self, currencyPair, rate, amount, lendingRate=None):
        vals = clean_locals(locals())
        return self.api_post("marginBuy", vals)

    def marginSell(self, currencyPair, rate, amount, lendingRate=None):
        vals = clean_locals(locals())
        return self.api_post("marginSell", vals)

    def getMarginPosition(self, currencyPair="all"):
        vals = clean_locals(locals())
        return self.api_post("getMarginPosition", vals)

    def closeMarginPosition(self, currencyPair):
        vals = clean_locals(locals())
        return self.api_post("closeMarginPosition", vals)

    def createLoanOffer(self, currency, amount, duration, autoRenew, lendingRate):
        vals = clean_locals(locals())
        return self.api_post("createLoanOffer", vals)

    def cancelLoanOffer(self, orderNumber):
        vals = clean_locals(locals())
        return self.api_post("cancelLoanOffer", vals)

    def returnOpenLoanOffers(self):
        return self.api_post("returnOpenLoanOffers")

    def returnActiveLoans(self):
        return self.api_post("returnActiveLoans")

    def returnLendingHistory(self, start=None, end=None, limit=None):
        vals = clean_locals(locals())
        return self.api_post("returnLendingHistory", vals)

    def toggleAutoRenew(self, orderNumber):
        vals = clean_locals(locals())
        return self.api_post("toggleAutoRenew", vals)
