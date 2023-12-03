import numpy as np


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

    def update(self, state, action, reward, next_state, next_action):
        predict = self.q_table[state, action]
        target = reward + self.gamma * self.q_table[next_state, next_action]
        self.q_table[state, action] += self.alpha * (target - predict)

    def reset(self):
        self.q_table = np.zeros((self.number_of_states, self.number_of_actions))

