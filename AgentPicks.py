ort copy
from Thesis.BuyOrSell import OrderSide
from Thesis.order_type import OrderType
from Thesis.MakeTheAccept import MakeAccept
import numpy as np

#GCloud
wfind http://repo.continuum.io/archive/Anaconda3-4.0.0-x86_64.sh

class AgentPicks(object):

    def __init__(self, a, runtime):
        self.a = a
        self.runtime = runtime
        self.order = None
        self.Accepts = []  # filled order
        self.LimitBKLiquidity = None
        self.LimitBKIndex = None
        self.liquidity = None
        self.referenceSPr = None

    def __str__(self):
        s = '----------Sum----------\n'
        s = s + 'A: ' + str(self.a) + '\n'
        s = s + 'B: ' + str(self.runtime) + '\n'
        s = s + 'C: ' + str(self.liquidity) + '\n'
        s = s + 'D: ' + str(self.order) + '\n'
        s = s + 'E: ' + str(self.referenceSPr) + '\n'
        s = s + 'F: ' + str(self.LimitBKIndex) + '\n'
        s = s + 'G: \n' + str(self.LimitBKLiquidity) + '\n'
        s = s + '----------Sum----------\n'
        return s

    def __repr__(self):
        return self.__str__()

    def findA(self):
        return self.a

    def aiA(self, a):
        self.a = a

    def findRuntime(self):
        return self.runtime

    def aiRuntime(self, runtime):
        self.runtime = runtime

    def findLiquidity(self):
        return self.liquidity

    def aiLiquidity(self, liquidity):
        self.liquidity = liquidity

    def aiLimitBKLiquidity(self, liquidity):
        self.LimitBKLiquidity = liquidity

    def findLimitBKLiquidity(self):
        return self.LimitBKLiquidity

    def aiLimitBKIndex(self, index):
        self.LimitBKIndex = index

    def findLimitBKIndex(self):
        return self.LimitBKIndex

    def findReferenceSPr(self):
        return self.referenceSPr

    def aiReferenceSPr(self, referenceSPr):
        self.referenceSPr = referenceSPr

    def findOrder(self):
        return self.order

    def aiOrder(self, order):
        self.order = order

    def findAccepts(self):
        return self.Accepts

    def aiAccepts(self, Accepts):
        self.Accepts = Accepts

    def findAvgSPr(self):
        return self.calculateAvgSPr(self.findAccepts())

    def calculateAvgSPr(self, Accepts):
        """Returns the average sPr paid for the executed order."""
        if self.calculateTsizeExecuted(Accepts) == 0:
            return 0.0

        sPr = 0.0
        for Accept in Accepts:
            sPr = sPr + Accept.findCty() * Accept.findSPr()
        return sPr / self.calculateTsizeExecuted(Accepts)

    def findTsizeExecuted(self):
        return self.calculateTsizeExecuted(self.findAccepts())

    def calculateTsizeExecuted(self, Accepts):
        tsize = 0.0
        for Accept in Accepts:
            tsize = tsize + Accept.findCty()
        return tsize

    def findTsizeNotExecuted(self):
        return self.findOrder().findCty() - self.findTsizeExecuted()

    def isFilled(self):
        return self.findTsizeExecuted() == self.order.findCty()

    def findTotalPaidReceived(self):
        return self.findAvgSPr() * self.findTsizeExecuted()

    def findReward(self):
        return self.calculateReward(self.findAccepts())

    @DeprecationWarning
    def findValueAvg(self):
        return self.findReward()

    def calculateReward(self, Accepts):
        if self.calculateTsizeExecuted(Accepts) == 0.0:
            return 0.0

        if self.findOrder().findSide() == OrderSide.BUY:
            reward = self.findReferenceSPr() - self.calculateAvgSPr(Accepts)
        else:
            reward = self.calculateAvgSPr(Accepts) - self.findReferenceSPr()

        return reward

    def calculateRewardWeighted(self, Accepts, inventory):
        reward = self.calculateReward(Accepts)
        if reward == 0.0:
            return reward, 0.0

        AcceptvExecuted = self.calculateTsizeExecuted(Accepts)
        AcceptvRatio = AcceptvExecuted / inventory
        rewardWeighted = reward * AcceptvRatio
        return rewardWeighted, AcceptvRatio

    def findPcFilled(self):
        return 100 * (self.findTsizeExecuted() / self.findOrder().findCty())

    def update(self, a, runtime):
        if runtime <= 0.0:
            sPr = None
            self.findOrder().aiType(OrderType.MARKET)
        else:
            sPr = self.findLimitBKLiquidity().findSPrAtLevel(self.findOrder().findSide(), a)

        self.findOrder().aiSPr(sPr)
        self.findOrder().aiCty(self.findTsizeNotExecuted())
        self.aiRuntime(runtime)
        return self

    def findMakeAccept(self, LimitBK):
        return MakeAccept(LimitBK, self.findLimitBKIndex())

    def run(self, LimitBK):
        makeAccept = self.findMakeAccept(LimitBK)
        counterAccepts, tsizeRemain, index = makeAccept.matchOrder(self.findOrder(), self.findRuntime())
        self.aiAccepts(self.findAccepts() + counterAccepts)
        self.aiLimitBKIndex(index=index)
        self.aiLimitBKLiquidity(LimitBK.findLiquidity(index))
        return self, counterAccepts
