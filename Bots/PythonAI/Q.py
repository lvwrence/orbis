import random
import pickle
import os
import atexit
from collections import defaultdict

DIRPATH = os.path.dirname(os.path.realpath(__file__))
Q_PICKLE_PATH = os.path.join(DIRPATH, "q.pickle")

class Q(object):
    def __init__(self):
        """Creates the state -> value dict."""
        self.load()
        self.alpha = 0.5
        self.epsilon = 0.25
        self.gamma = 0.3
        self.last_action = None
        self.last_state = None

        atexit.register(self.save)

    def load(self):
        self.q = defaultdict(int)
        if os.path.exists(Q_PICKLE_PATH):
            with open(Q_PICKLE_PATH, "rb") as q_file:
                self.q.update(pickle.load(q_file))

    def save(self):
        with open(Q_PICKLE_PATH, "wb") as q_file:
            pickle.dump(self.q, q_file)

    def update(self, new_state, all_actions_in_new_state, reward):
        if not self.last_state or not self.last_action or not all_actions_in_new_state:
            return

        # update algorithm according to formula
        max_q_for_new_state = max(self.q[new_state, action] for action in all_actions_in_new_state)
        self.q[self.last_state, self.last_action] += self.alpha * (reward + (self.gamma * max_q_for_new_state) - self.q[self.last_state, self.last_action])

    def choose_action(self, state, actions):
        action = None
        if random.random() > self.epsilon:
            action = max(actions, key=lambda action: self.q[state, action])
        else:
            action = random.sample(actions, 1)[0]
        self.last_action = action
        self.last_state = state
        return action
