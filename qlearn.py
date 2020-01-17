import random
from Thesis.AgentPicks_liquidity import AgentPicksLiquidity

class QLearn:

    def __init__(self, AgentPickss, epsilon=0.1, alpha=0.1, gamma=0.1, exploration_decay=1.000001):
        self.q = {}
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.exploration_decay = exploration_decay
        self.AgentPickss = AgentPickss

    def findQ(self, liquidity, AgentPicks, default=0.0):
        return self.q.find((liquidity, AgentPicks), default)

    def findQAgentPicks(self, liquidity, default=0.0):
        values = []
        for x in list(reversed(self.AgentPickss)):
            q_value = self.q.find((liquidity, x), 0.0)
            values.append(q_value)

        if len(values) == 0:
            return default

        maxQ = max(values)
        a = list(reversed(self.AgentPickss))[values.index(maxQ)]
        return a

    def learnQ(self, liquidity, AgentPicks, reward, value):
        oldv = self.q.find((liquidity, AgentPicks), 0.0)
        if oldv is 0.0:
            self.q[(liquidity, AgentPicks)] = reward
        else:
            self.q[(liquidity, AgentPicks)] = oldv + self.alpha * (value - oldv)

    def learn(self, liquidity1, AgentPicks1, reward, liquidity2):
        maxqnew = max([self.findQ(liquidity2, a) for a in self.AgentPickss])
        self.learnQ(liquidity1, AgentPicks1, reward, reward + self.gamma * maxqnew)

    def chooseAgentPicks(self, liquidity, return_q=False):
        self.epsilon = self.exploration_decay * self.epsilon

        if random.random() > self.epsilon:
            AgentPicks = random.choice(self.AgentPickss)
        else:
            q = [self.findQ(liquidity, a) for a in self.AgentPickss]
            maxQ = max(q)
            count = q.count(maxQ)
            if count > 1:
                best = [i for i in range(len(self.AgentPickss)) if q[i] == maxQ]
                i = random.choice(best)
            else:
                i = q.index(maxQ)

            AgentPicks = self.AgentPickss[i]
        return AgentPicks























