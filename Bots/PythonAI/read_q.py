import os
import pickle
from pprint import pprint

DIRPATH = os.path.dirname(os.path.realpath(__file__))
Q_PICKLE_PATH = os.path.join(DIRPATH, "q.pickle")

with open(Q_PICKLE_PATH, 'rb') as q_file:
    d = pickle.load(q_file)
    pprint(d)
