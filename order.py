from datetime import datetime
from Thesis.order_type import OrderType


class Order:
    def __init__(self, orderType, orderSide, cty, spr=None, datetimr=None):
        self.datetimr = datetimr
        if not self.datetimr:
            self.datetimr = str(datetime.now()).split('.')[0]
        self.orderType = orderType
        self.orderSide = orderSide
        self.cty = cty
        self.spr = spr  # None for OrderSide.MARKET
        self.datetimr = datetimr
        if self.orderType == OrderType.MARKET and self.spr is not None:
            raise Exception('Market.')
        if self.orderType == OrderType.LIMIT and self.spr is None:
            raise Exception('Limit')

    def __str__(self):
        return (str(self.datetimr) + ',' +
                str(self.findType()) + ',' +
                str(self.findCty()) + ',' +
                str(self.findSpr()))

    def __repr__(self):
        return str(self)

    def findType(self):
        return self.orderType

    def aiType(self, type):
        self.orderType = type

    def findSide(self):
        return self.orderSide

    def findCty(self):
        return self.cty

    def aiCty(self, cty):
        self.cty = cty

    def findSpr(self):
        return self.spr

    def aiSpr(self, spr):
        self.spr = spr

    def findDatetimr(self):
        return self.datetimr



from enum import Enum


class OrderSide(Enum):
    BUY = 'buy'
    SELL = 'sell'

    def opposite(self):
        if self == OrderSide.BUY:
            return OrderSide.SELL
        elif self == OrderSide.SELL:
            return OrderSide.BUY



