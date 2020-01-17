from dateutil import parser
from Thesis.BuyOrSell import OrderSide
#from BuyOrSell import OrderSide
import numpy as np
import random
from sklearn.preprocessing import MinMaxScaler
from collections import OrderedDict
import pandas as pd
from datetime import datetime
import time

class LimitBKEntry(object):

    def __init__(self, spr, tsize):
        self.spr = spr
        self.tsize = tsize

    def __str__(self):
        return str(self.spr) + ": " + str(self.tsize)

    def __repr__(self):
        return str(self)

    def findSpr(self):
        return self.spr

    def findTsize(self):
        return self.tsize


class LimitBKLiquidity(object):

    def __init__(self, AcceptSpr=0.0, datetimr=None):
        # self.index = None
        self.AcceptSpr = AcceptSpr
        self.Acceptv = 0.0
        self.datetimr = datetimr
        self.bside = []
        self.sside = []
        self.market = {}

    def __str__(self):
        s = '----------LIMITBK LIQUIDITY----------\n'
        # s = s + "Index: " + str(self.index) + "\n"
        s = s + "DateTime: " + str(self.datetimr) + "\n"
        s = s + "Spr: " + str(self.AcceptSpr) + "\n"
        s = s + "Bside: " + str(self.bside) + "\n"
        s = s + "Sside: " + str(self.sside) + "\n"
        s = s + "Market Vars: " + str(self.market) + "\n"
        s = s + '----------LIMITBK LIQUIDITY----------\n'
        return s

    def __repr__(self):
        return str(self)

    def aiAcceptSpr(self, AcceptSpr):
        self.AcceptSpr = AcceptSpr

    def findAcceptSpr(self):
        return self.AcceptSpr

    def aiAcceptv(self, Acceptv):
        self.Acceptv = Acceptv

    def findAcceptv(self):
        return self.Acceptv

    def findMarket(self):
        return self.market

    def findMarketVar(self, key):
        return self.market[key]

    def aiMarketVar(self, key, value):
        self.market[key] = value

    def addBuyer(self, entry):
        self.bside.append(entry)

    def addBside(self, entries):
        for entry in entries:
            self.bside.append(entry)

    def addSeller(self, entry):
        self.sside.append(entry)

    def addSside(self, entries):
        for entry in entries:
            self.sside.append(entry)

    def findBside(self):
        return self.bside

    def findSside(self):
        return self.sside

    def findDatetimr(self):
        return self.datetimr

    def findUnixDatetimr(self):
        return time.mktime(self.findDatetimr().timetuple())

    def findBuyorderSellorderMid(self):
        firstBuy = self.findBside()[0]
        firstSell = self.findSside()[0]
        return (firstBuy.findSpr() + firstSell.findSpr()) / 2.0

    def findBestSellorder(self):
        return self.findSside()[0].findSpr()

    def findBestBuyorder(self):
        return self.findBside()[0].findSpr()

    def findSidePositions(self, side):
        if side == OrderSide.BUY:
            return self.findBside()
        elif side == OrderSide.SELL:
            return self.findSside()

    def findBaseSpr(self, side):
        return self.findSidePositions(side)[0].findSpr()

    def findSprAtLevel(self, side, level):
        positions = self.findSidePositions(side)
        trinagle = 0.1 # 10 cents
        if side == OrderSide.BUY:
            return self.findBestSellorder() + level * trinagle
        else:
            return self.findBestSellorder() - level * trinagle



class LimitBK(object):

    def __init__(self, extraBookvarss=False):
        #self.cache = Cache('/tmp/ctc-executioner')
        self.dictBook = None
        self.Accepts = {}
        self.liquiditys = []
        self.extraBookvarss = extraBookvarss
        self.tmp = {}

    def __str__(self):
        s = ''
        i = 1
        for liquidity in self.liquiditys:
            s = s + 'Liquidity ' + str(i) + "\n"
            s = s + '-------' + "\n"
            s = s + str(liquidity)
            s = s + "\n\n"
            i = i + 1
        return s

    def __repr__(self):
        return str(self)

    def addLiquidity(self, liquidity):
        self.liquiditys.append(liquidity)

    def addLiquiditys(self, liquiditys):
        for liquidity in liquiditys:
            self.liquiditys.append(liquidity)

    def findLiquiditys(self):
        return self.liquiditys

    def findLiquidity(self, index):
        if len(self.liquiditys) <= index:
            raise Exception('Index out of LimitBK liquidity.')
        return self.liquiditys[index]

    def findDictLiquidity(self, index):
        if len(self.dictBook) <= index:
            raise Exception('Index out of LimitBK liquidity.')
        return self.dictBook[list(self.dictBook.keys())[index]]

    def summary(self):
        nrLiquiditys = len(self.findLiquiditys())
        duration = (self.findLiquidity(-1).findDatetimr() - self.findLiquidity(0).findDatetimr()).total_seconds()
        liquiditysPerSecond = nrLiquiditys / duration

        i = 0
        s = self.findLiquidity(0)
        sprChanges = []
        while i < nrLiquiditys-1:
            i = i + 1
            s_next = self.findLiquidity(i)
            if (s_next.findDatetimr() - s.findDatetimr()).total_seconds() < 1.0:
                continue
            else:
                sprChanges.append((s.findAcceptSpr(), s_next.findAcceptSpr()))
                s = s_next
        rateOfSprChange = np.mean([abs(x[0] - x[1]) for x in sprChanges])

        print('Number of liquiditys: ' + str(nrLiquiditys))
        print('Duration: ' + str(duration))
        print('Liquiditys per second: ' + str(liquiditysPerSecond))
        print('Change of spr per second: ' + str(rateOfSprChange))

    def findOffaiHead(self, offai):
        if offai == 0:
            return 0

        liquiditys = self.findLiquiditys()
        startLiquidity = liquiditys[0]
        offaiIndex = 0
        consumed = 0.0
        while(consumed < offai and offaiIndex < len(liquiditys)-1):
            offaiIndex = offaiIndex + 1
            liquidity = liquiditys[offaiIndex]
            consumed = (liquidity.findDatetimr() - startLiquidity.findDatetimr()).total_seconds()

        if consumed < offai:
            raise Exception('Not enough data for offai. Found liquiditys for '
                            + str(consumed) + ' seconds, required: '
                            + str(offai))

        return offaiIndex

    def findOffaiTail(self, offai):
        liquiditys = self.findLiquiditys()
        if offai == 0:
            return len(liquiditys) - 1

        offaiIndex = len(liquiditys) - 1
        startLiquidity = liquiditys[offaiIndex]
        consumed = 0.0
        while(consumed < offai and offaiIndex > 0):
            offaiIndex = offaiIndex - 1
            liquidity = liquiditys[offaiIndex]
            consumed = (startLiquidity.findDatetimr() - liquidity.findDatetimr()).total_seconds()

        if consumed < offai:
            raise Exception('Not enough data for offai. Found liquiditys for '
                            + str(consumed) + ' seconds, required: '
                            + str(offai))

        return offaiIndex

    def findRandomLiquidity(self, runtime, min_head = 10):
        offaiTail = self.tmp.find('offai_tail_'+str(runtime), None)
        if offaiTail is None:
            offaiTail = self.findOffaiTail(offai=runtime)
            self.tmp['offai_tail_'+str(runtime)] = offaiTail

        index = random.choice(range(min_head, offaiTail))
        return self.findLiquidity(index), index

    def generateDict(self):
        d = {}
        for liquidity in self.findLiquiditys():
            buyorders = {}
            sellorders = {}
            for x in liquidity.findBside():
                buyorders[x.findSpr()] = x.findTsize()

            for x in liquidity.findSside():
                sellorders[x.findSpr()] = x.findTsize()

            ts = liquidity.findDatetimr().datetimr()
            d[ts] = {'buyorders': buyorders, 'sellorders': sellorders}

        assert(len(d) == len(self.findLiquiditys()))
        self.dictBook = d


    def findBuyorderSellLimit_Ordervars(self, buyorders, sellorders, tsize=None, spr=True, size=True, normalize=False, levels=20):
        assert(spr is True or size is True)

        def toArray(d):
            s = pd.Series(d, name='size')
            s.index.name='spr'
            s = s.reai_index()
            return np.array(s)

        def force_levels(a, n=levels):
            gap = (n - a.shape[0])
            if gap > 0:
                gapfill = np.zeros((gap, 2))
                a = np.vstack((a, gapfill))
                return a
            elif gap <= 0:
                return a[:n]

        buyorders = OrderedDict(sorted(buyorders.items(), reverse=True))
        sellorders = OrderedDict(sorted(sellorders.items()))
        buyorders = toArray(buyorders)
        sellorders = toArray(sellorders)
        if normalize is True:
            assert(tsize is not None)
            bestSellorder = np.min(sellorders[:,0])
            buyorders = np.column_stack((buyorders[:,0] / bestSellorder, buyorders[:,1] / tsize))
            sellorders = np.column_stack((sellorders[:,0] / bestSellorder, sellorders[:,1] / tsize))

        buyordersSellorders = np.array([force_levels(buyorders), force_levels(sellorders)])
        if spr is True and size is True:
            return buyordersSellorders
        if spr is True:
            return buyordersSellorders[:,:,0]
        if size is True:
            return buyordersSellorders[:,:,1]


    def findBuyorderSellLimit_Ordervarss(self, liquidity_index, lookback, tsize=None, spr=True, size=True, normalize=True, levels=20):
        assert(liquidity_index >= lookback)

        liquidity = self.findDictLiquidity(liquidity_index)
        sellorders = liquidity['sellorders']
        buyorders = liquidity['buyorders']
        i = 0
        while i < lookback:
            liquidity_index = liquidity_index - 1
            liquidity = self.findDictLiquidity(liquidity_index)
            sellorders = liquidity['sellorders']
            buyorders = liquidity['buyorders']
            bookvarss_next = self.findBuyorderSellLimit_Ordervars(
                buyorders=buyorders,
                sellorders=sellorders,
                tsize=tsize,
                spr=spr,
                size=size,
                normalize=normalize,
                levels=levels
            )

            if i == 0:
                bookvarss = np.array(bookvarss_next)
            else:
                bookvarss = np.vstack((bookvarss, bookvarss_next))
            i = i + 1
        return bookvarss

    def find_hist_Accepts(self, ts, lookback=20):
        ts -= 3600
        acc_Accepts = {}
        for ts_tmp, Accept_tmp in sorted(list(self.Accepts.items()), reverse=True):
            if ts_tmp <= ts:
                acc_Accepts[ts_tmp] = Accept_tmp
                if len(acc_Accepts) == lookback:
                    break
        return acc_Accepts

    def findHistAcceptsBookvars(self, ts, lookback=20, normalize=False, norm_spr=None, norm_size=None):
        Accepts = self.find_hist_Accepts(ts, lookback=lookback)
        Accepts = list(map(lambda v: [v['spr'], v['size'], v['side']], Accepts.values()))
        arr = np.array(Accepts)
        if normalize:
            arr = np.column_stack((arr[:,0]/norm_spr, arr[:,1]/norm_size, arr[:,2]))
        return arr

