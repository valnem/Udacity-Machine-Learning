import random
import pdb
import math
import gc

class Qlearn:
    def __init__(self, actions,epsilon = 0.1, alpha = 0.7, gamma = 0.1):
       
        self.q = {}
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.actions = actions    
        
    def getQ(self, state, action):
        return self.q.get((state, action), -1.0)

    def chooseAction(self, state):
        if random.random() < self.epsilon:
            action = random.choice(self.actions)
        else:
            self.valid_actions = self.valid_Actions(state)
            q = [self.getQ(state, a) for a in self.valid_actions]
            maxQ = max(q)
            count = q.count(maxQ)
            if count > 1:
                best = [i for i in range(len(self.valid_actions)) if q[i] == maxQ]
                i = random.choice(best)               
            else:
                i = q.index(maxQ)
               
            action = self.valid_actions[i]
        return action

    def learn(self, laststate, lastaction, reward, state):
##        self.epsilon = 0.1
##        self.alpha = 0.4 #1/float(time+1)
##        self.gamma = 0.5 #1 - 1/float(time+1)
        
        self.valid_actions = self.valid_Actions(state)
        oldq = self.q.get((laststate,lastaction), None)
        
        if oldq is None:
            self.q[(laststate,lastaction)] = reward
        else:
            maxQ = max([self.getQ(state, a) for a in self.valid_actions])
            self.q[(laststate,lastaction)] = oldq + self.alpha * (reward + self.gamma * maxQ - oldq )
        
         
    def valid_Actions(self, sense):
        act = []
        move_okay = True
        #pdb.set_trace()
        light = sense[0]
        for action in self.actions:
            if action == 'forward':
                if light != 'green':
                    move_okay = False
            elif action == 'left':
                if light == 'green' and (sense[1] == None or sense[1] == 'left'):
                    move_okay = True
                else:
                    move_okay = False
            elif action == 'right':
                if light == 'green' or sense[2] != 'straight':
                    move_okay = True
                if light == 'red' and (sense[1] != 'left' and sense[2] != 'straight'):
                    move_okay = True
                else:
                    move_okay = False

            if move_okay:
                act.append(action)
            else: act.append(None)
            
        #pdb.set_trace() 
        return list(set(act))
        
