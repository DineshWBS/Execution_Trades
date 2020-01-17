from Thesis.Accept import Accept
from Thesis.order import Order
from Thesis.order_type import OrderType
from Thesis.BuyOrSell import OrderSide
import copy
import numpy as np

class MakeAccept(object):

    def __init__(self, LimitBK, index=0, maxRuntime=100):
        self.LimitBK = LimitBK
        self.index = index
        self.maxRuntime = maxRuntime
        self.matches = ai()
        self.recordMatches = False

    def _removePosition(self, side, spr, tside):
        if self.recordMatches == True:
            self.matches.add((side, spr, tside))

    def _isRemoved(self, side, spr, tside):
        return (side, spr, tside) in self.matches

    def aiIndex(self, index):
        self.index = index

    def matchLimitOrder(self, order, LimitBKLiquidty):

        if order.findSide() == OrderSide.BUY:
            bookSide = LimitBKLiquidty.findSside()
        else:
            bookSide = LimitBKLiquidty.findBside()

        def isMatchingPosition(p):
            if order.findSide() == OrderSide.BUY:
                return bookSide[sidePosition].findSpr() <= order.findSpr()
            else:
                return bookSide[sidePosition].findSpr() >= order.findSpr()

        partialAccepts = []
        remaining = order.findCty()
        sidePosition = 0
        while len(bookSide) > sidePosition and isMatchingPosition(sidePosition) and remaining > 0.0:
            p = bookSide[sidePosition]
            spr = p.findSpr()
            tside = p.findTside()
#Must be matched with another trade.
            if self._isRemoved(side=order.findSide(), spr=spr, tside=tside):
                continue

            if not partialAccepts and tside >= order.findCty():
                t = Accept(orderSide=order.findSide(), orderType=OrderType.LIMIT, cty=remaining, spr=spr, datetimr=LimitBKLiquidty.findDatetimr())
                return [t]
            else:
                t = Accept(orderSide=order.findSide(), orderType=OrderType.LIMIT, cty=min(tside, remaining), spr=spr, datetimr=LimitBKLiquidty.findDatetimr())
                partialAccepts.append(t)
                sidePosition = sidePosition + 1
                remaining = remaining - tside

                if sidePosition == len(bookSide) - 1:
                    average_tside = np.mean([x.findCty() for x in partialAccepts])
                    if average_tside == 0.0:
                        average_tside = 0.5
                    derivative_spr = abs(np.mean(np.gradient([x.findSpr() for x in partialAccepts])))
                    if derivative_spr == 0.0:
                        derivative_spr = 10.0
                    while remaining > 0.0:
                        if order.findSide() == OrderSide.BUY:
                            spr = spr + derivative_spr
                            if spr > order.findSpr():
                                break
                        elif order.findSide() == OrderSide.SELL:
                            spr = spr - derivative_spr
                            if spr < order.findSpr():
                                break

                        tside = min(average_tside, remaining)
                        partialAccepts.append(Accept(orderSide=order.findSide(), orderType=OrderType.LIMIT, cty=tside, spr=spr, datetimr=LimitBKLiquidty.findDatetimr()))
                        remaining = remaining - tside

        return partialAccepts

    def matchMarketOrder(self, order, LimitBKLiquidty):
        if order.findSide() == OrderSide.BUY:
            bookSide = LimitBKLiquidty.findSside()
        else:
            bookSide = LimitBKLiquidty.findBside()

        partialAccepts = []
        remaining = order.findCty()
        sidePosition = 0
        spr = 0.0
        while len(bookSide) > sidePosition and remaining > 0.0:
            p = bookSide[sidePosition]
            derivative_spr = p.findSpr() - spr
            spr = p.findSpr()
            tside = p.findTside()
            if not partialAccepts and tside >= order.findCty():
                return [Accept(orderSide=order.findSide(), orderType=OrderType.MARKET, cty=remaining, spr=spr, datetimr=LimitBKLiquidty.findDatetimr())]
            else:
                tsideExecute = min(tside, remaining)
                partialAccepts.append(Accept(orderSide=order.findSide(), orderType=OrderType.MARKET, cty=tsideExecute, spr=spr, datetimr=LimitBKLiquidty.findDatetimr()))
                sidePosition = sidePosition + 1
                remaining = remaining - tsideExecute

        return partialAccepts

#If you modify the data its going to change it for next time you run. copy it? Seems to increase runtime :( alot
    def matchOrder(self, order, seconds=None):
        order = copy.deepcopy(order)
        i = self.index
        remaining = order.findCty()
        Accepts = []

        while len(self.LimitBK.findLiquidtys()) - 1 > i and remaining > 0:
            LimitBKLiquidty = self.LimitBK.findLiquidty(i)

            if seconds is not None:
                t_start = self.LimitBK.findLiquidty(self.index).findDatetimr()
                t_now = LimitBKLiquidty.findDatetimr()
                t_triangle = (t_now - t_start).total_seconds()
                if t_triangle >= seconds:
                    break

            if order.findType() == OrderType.LIMIT:
                counterAccepts = self.matchLimitOrder(order, LimitBKLiquidty)
            elif order.findType() == OrderType.MARKET:
                counterAccepts = self.matchMarketOrder(order, LimitBKLiquidty)
            elif order.findType() == OrderType.LIMIT_T_MARKET:
                if seconds is None:
                    raise Exception(str(OrderType.LIMIT_T_MARKET) + 'Problem')
                counterAccepts = self.matchLimitOrder(order, LimitBKLiquidty)
            else:
                raise Exception('Error')

            if counterAccepts:
                Accepts = Accepts + counterAccepts
                for counterAccept in counterAccepts:
                    remaining = remaining - counterAccept.findCty()
                order.aiCty(remaining)
            else:
            i = i + 1

        if remaining > 0.0 and (order.findType() == OrderType.LIMIT_T_MARKET or order.findType() == OrderType.MARKET):
            if not len(self.LimitBK.findLiquidtys()) > i:
                raise Exception('Not enough data.')

            LimitBKLiquidty = self.LimitBK.findLiquidty(i)
            counterAccepts = self.matchMarketOrder(order, LimitBKLiquidty)
            if not counterAccepts:
                raise Exception('Remaining')
            Accepts = Accepts + counterAccepts
            for counterAccept in counterAccepts:
                remaining = remaining - counterAccept.findCty()
            order.aiCty(remaining)
        return Accepts, remaining, i-1

