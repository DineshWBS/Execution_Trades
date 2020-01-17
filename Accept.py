from datetime import datetime

class Accept:
    def __init__(self, orderSide, orderType, cty, spr, fee=0.0, datetimr=str(datetime.now()).split('.')[0]):
        self.orderSide = orderSide
        self.orderType = orderType
        self.cty = cty
        self.spr = spr
        self.datetimr = datetimr

    def __str__(self):
        return (str(self.datetimr) + ',' +
                str(self.findSide()) + ',' +
                str(self.findType()) + ',' +
                str(self.findCty()) + ',' +
                str(self.findSpr()) + ',' +

    def __repr__(self):
        return str(self)

    def findSide(self):
        return self.orderSide

    def findType(self):
        return self.orderType

    def findCty(self):
        return self.cty

    def aiCty(self, cty):
        self.cty = cty

    def findSpr(self):
        return self.spr

    def findFee(self):
        return self.fee

    def findDatetimr(self):
        return self.datetimr

