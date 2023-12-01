import numpy as np
import random


class SARSA:
    def __init__(self, alpha, gamma, epsilon, number_of_states, number_of_actions):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.number_of_states = number_of_states
        self.number_of_actions = number_of_actions
        self.q_table = np.zeros((self.number_of_states, self.number_of_actions))

    def choose_action(self, state):
        if np.random.uniform(0, 1) < self.epsilon:
            action = np.random.choice(self.number_of_actions)
        else:
            action = np.argmax(self.q_table[state, :])
        return action

    def learn(self, state, action, reward, next_state, next_action):
        predict = self.q_table[state, action]
        target = reward + self.gamma * self.q_table[next_state, next_action]
        self.q_table[state, action] += self.alpha * (target - predict)

# def run(self):
#     sarsa = SARSA(alpha=0.1, gamma=0.9, epsilon=0.1, number_of_states=NUM_STATES, number_of_actions=NUM_ACTIONS)
#     current_state = self.get_current_state()
#
#     while running:
#         # existing code for simulation
#         action = sarsa.choose_action(current_state)
#         # perform action and get new state and reward
#         next_state = self.get_next_state()
#         reward = self.calculate_dti() # Your DTI based reward
#         next_action = sarsa.choose_action(next_state)
#         sarsa.learn(current_state, action, reward, next_state, next_action)
#         current_state = next_state
#
#         # rest of your loop