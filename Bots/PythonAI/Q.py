import random
import json
import os
import atexit
from collections import defaultdict

DIRPATH = os.path.dirname(os.path.realpath(__file__))
Q_JSON_PATH = os.path.join(DIRPATH, "q.json")

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
        if os.path.exists(Q_JSON_PATH):
            with open(Q_JSON_PATH) as q_file:
                self.q = json.load(q_file)
        else:
            self.q = defaultdict(int)

    def save(self):
        with open(Q_JSON_PATH, "w") as q_file:
            json.dump(self.q, q_file)

    def update(self, new_state, all_actions_in_new_state, reward):
        if not self.last_state or not self.last_action:
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
