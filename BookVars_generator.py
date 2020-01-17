from Thesis.LimitBK import LimitBK
import numpy as np
import pandas as pd
import os

import WRDS
db = wrds.Connection()


#connecting to wharton. book = wrds file

book = file #.sh/wrds/rt_IBMDATA (remember to change to GS and Ford}
tmp='bookvars.tsv'
LimitBK = LimitBK()
LimitBK.loadFromEvents(book)
liquiditys = LimitBK.findLiquiditys()


def liquidityDiff(start, end):
    consumed = (end.findDatetimr() - start.findDatetimr()).total_seconds()
    return consumed


def findPastLiquidity(i, t):
    endLiquidity = liquiditys[i]
    liquidity = endLiquidity
    while(liquidityDiff(liquidity, endLiquidity) < t):
        i = i - 1
        if i < 0:
            raise Exception("Somewhere error")
        liquidity = liquiditys[i]
    return i


def traverse(f, g, default=0.0, t=60):
    startLiquidity = liquiditys[0]
    consumed = 0.0
    for i in range(len(liquiditys)):
        liquidity = liquiditys[i]
        consumed = liquidityDiff(startLiquidity, liquidity)
        if consumed < t:
            g(i, default)
        else:
            pastLiquidity = findPastLiquidity(i, t)
            g(i, f(pastLiquidity, i+1))


def calcAcceptv(start, end):
    vol = 0.0
    for j in range(start, end):
        tempLiquidity = liquiditys[j]
        vol = vol + tempLiquidity.findAcceptv()
    return vol


def calcStdSpr(start, end):
    sprs = map(lambda x: liquiditys[x].findAcceptSpr(), range(start, end))
    return np.std(list(sprs))


def calcMeanSpr(start, end):
    sprs = map(lambda x: liquiditys[x].findAcceptSpr(), range(start, end))
    return np.mean(list(sprs))


def toFile(i, x):
    output = str(x) + '\n'
    with open(tmp, 'a') as fa:
        fa.write(output)

# def askVol(i, x):
#   vol = ask
#

def printBookvars(f, default=0.0, t=60):
    traverse(f, lambda i, x: print(str((i, x))), default, t)


printBookvars(calcStdSpr)

