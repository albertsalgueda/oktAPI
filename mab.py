from application import *
import numpy as np

class SimulationAgent(object):

  def __init__(self, env, initial_q, initial_visits, max_iterations):
    self.env = env
    self.iterations = max_iterations
    self.initial_q = initial_q
    self.initial_visits = initial_visits

    self.q_values = np.ones(self.env.k_arms) * self.initial_q
    self.arm_counts = np.ones(self.env.k_arms) * self.initial_visits
    self.arm_rewards = np.zeros(self.env.k_arms)
    
    self.rewards = [0.0]
    self.cum_rewards = [0.0]

  def act(self):
    count = 0
    old_estimate = 0.0
    arm = np.argmax(self.q_values)
    reward = self.env.take_action(arm,self.q_values)
    print(f'The rewards at timestamp {self.env.current_time} is {reward}')
    #sum one to the arm that was choosen 
    self.arm_counts[arm] = self.arm_counts[arm] + 1
    #assign rewards for all arms
    for arm in range(self.env.k_arms):
      self.arm_rewards[arm] = self.arm_rewards[arm] + reward[arm]
      self.q_values[arm] = self.q_values[arm] + (1/self.arm_counts[arm]) * (reward[arm] - self.q_values[arm])
    #print(self.q_values)
    self.rewards.append(sum(reward))
    count += 1
    current_estimate = old_estimate + (1/count)*(sum(reward)-old_estimate)
    self.cum_rewards.append(current_estimate)
    old_estimate = current_estimate

    return {"arm_counts": self.arm_counts, "rewards": self.rewards, "cum_rewards": self.cum_rewards}
