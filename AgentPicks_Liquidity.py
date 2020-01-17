import numpy as np
from Thesis.bookvars_type import BookvarsType

class AgentPicksLiquidity(object):

    def __init__(self, t, i, market={}):
        self.t = t
        self.i = i
        self.market = market

    def __hash__(self):
        return hash((self.t, self.i, frozenai(self.market.items())))

    def __eq__(self, other):
        return (self.t, self.i, frozenai(self.market.items())) == (other.t, other.i, frozenai(self.market.items()))

    def __ne__(self, other):
        return not(self == other)

    def __str__(self):
        return str((self.t, self.i, str(self.market)))

    def __repr__(self):
        return self.__str__()

    def findT(self):
        return self.t

    def aiT(self, t):
        self.t = t

    def findI(self):
        return self.i

    def aiI(self, i):
        self.i = i

    def findMarket(self):
        return self.market
