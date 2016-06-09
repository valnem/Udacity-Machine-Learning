import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import qlearn
import pdb
import matplotlib
import pylab as pl
import numpy
import pandas as pd
import gc

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env, trial):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.ql = qlearn.Qlearn(actions = Environment.valid_actions, epsilon=0.1, alpha=0.7, gamma=0.1)
        self.lastAction = None
        self.sr = []

        # Track number of times agent reaches destination
        self.trials = trial
        self.reach_dest = 0
        self.fault_reach = 0
        self.current_trial = 1
        self.last_success = 0
     
    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.destination = self.env.agent_states[self]['destination']
        self.start = self.env.agent_states[self]['location']
        self.lastState = None
        self.old_reward = 0
        

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        
        deadline = self.env.get_deadline(self)
        location = self.env.agent_states[self]['location']
        
        
        # TODO: Update state
        self.state = (inputs['light'], inputs['oncoming'],inputs['left'], self.next_waypoint )  
        
        # TODO: Select action according to your policy
        action = self.ql.chooseAction(self.state)
        
        # Execute action and get reward
        reward = self.env.act(self, action)
        
        # TODO: Learn policy based on state, action, reward
        if self.lastState is not None:
            self.ql.learn(self.lastState,self.lastAction,self.old_reward, self.state)

        self.lastAction = action
        self.lastState = self.state
        self.old_reward = reward
        
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]

        if self.env.agent_states[self]['deadline'] <= 0:#location != self.destination and deadline == 0:
            self.fault_reach += 1            
            if self.current_trial < self.trials:
                self.current_trial += 1
        if self.env.done and self.env.agent_states[self]['deadline'] > 0:
            #pdb.set_trace()
            self.reach_dest += 1
            self.sr.append(round(float(self.reach_dest)/float(self.current_trial), 3))
            if self.current_trial < self.trials:
                self.current_trial += 1
            if self.current_trial > 91:
                self.last_success += 1
        self.env.status_text += self.statistics()
       
    def statistics(self):
        if self.current_trial == 0:
            success_rate = 0
          
            
        else:
            success_rate = "{}/{} = %{}".format(self.reach_dest, self.current_trial, (round(float(self.reach_dest)/float(self.current_trial), 3))*100)

        if self.current_trial < 90:
            text = "\nReach/Trials: %s, Missed %s" % (success_rate,self.fault_reach)
        else:            
            text = "\nReach/Trials: %s, Missed %s, passed in Last 10 (Good if >= 7):  %s \n" % (success_rate,self.fault_reach, self.last_success)
        return text


def run():
    """Run the agent for a finite number of trials."""
    
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent, trial = 100)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track            

    # Now simulate it
    sim = Simulator(e, update_delay=0.00001)  # reduce update_delay to speed up simulation
    sim.run(n_trials = 100)  # press Esc or close pygame window to quit
                        
    Plotting(a.sr)
        
def Plotting(total):
        import numpy as np
        pl.style.use('seaborn-whitegrid')
        pl.figure(1)
        pl.scatter(np.linspace(0,len(total), len(total)), total)
        pl.xlabel('trials')
        pl.ylabel('success_rate, %')
        pl.title('Succes vs Trials (passed/trials)')
        pl.pause(3)
        pl.close()
        
if __name__ == '__main__':
    run()
