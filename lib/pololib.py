from . import poloapi, ensure
from .util import dt_min, seconds_between, ci_rate, pert
from datetime import datetime, timedelta
import time
from functools import partial
import json
import sys

typeDateTime = ensure.makeTypeEnsurer(poloapi.strToDT, 'datetime')

def handleBeginEndCall(begin, end, f, **keywords):
    if(begin and end):
        return f(start=begin, end=end, **keywords)
    elif(begin and not end):
        return f(start=begin, **keywords)
    elif(not begin and end):
        return f(end=end, **keywords)
    else:
        return f(**keywords)

class poloniex:
    def __init__(self, apikey, secret):
        self.api = poloapi.poloniex(apikey, secret)

    def getLendingHistory(self,
            begin = None,
            end   = None):

        """ Get lending history from Poloniex. If begin or end is not
            specified, its most extreme value is assumed.

            Optional keyword arguments:
            begin - a datetime of the oldest history to retrieve
            end - a datetime of the newest history to retrieve
        """

        # TODO: implement a local cache
        raw = handleBeginEndCall(begin, end, self.api.returnLendingHistory)

        return ensure.listOf(raw=raw, path="lendingHistory",
            ensurer=partial(ensure.dictOf, ensureRest=ensure.fail, ensurers={
                "id": ensure.typeInt,
                "autoRenew": ensure.typeInt,
                "duration": ensure.typeFloat,
                "rate": ensure.typeFloat,
                "amount": ensure.typeFloat,
                "interest": ensure.typeFloat,
                "fee": ensure.typeFloat,
                "earned": ensure.typeFloat,
                "open": typeDateTime,
                "close": typeDateTime,
                "currency": ensure.typeString}))

    def getActiveLoans(self,
            begin = None,
            end   = None):

        """ Get active loans on Poloniex. If begin or end is not
            specified, its most extreme value is assumed.
            Returns a dict where the key "provided" has all the
            loans the user has provided and the key "used" has
            all the loans that the user is using on margin.
        """

        raw = handleBeginEndCall(begin, end, self.api.returnActiveLoans)

        typeActiveLoanList = partial(ensure.listOf,
                ensurer=partial(ensure.dictOf, ensureRest=ensure.fail,
                    ensurers={
                        "id": ensure.typeInt,
                        "currency": ensure.typeString,
                        "duration": ensure.typeFloat,
                        "rate": ensure.typeFloat,
                        "amount": ensure.typeFloat,
                        "autoRenew": ensure.typeInt,
                        "date": typeDateTime,
                        "fees": ensure.typeFloat}))

        return ensure.dictOf(raw=raw, path="activeLoans",
                ensureRest=ensure.fail, ensurers={
                    "provided": typeActiveLoanList,
                    "used": typeActiveLoanList})
