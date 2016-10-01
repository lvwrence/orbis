from PythonClientAPI.libs.Game import PointUtils
from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.Entities import *
from PythonClientAPI.libs.Game.World import *

import random

MOVE = 0
SHOOT = 1
PICKUP = 2
SHIELD = 3

def get_possible_actions(enemy_units):
    # append dem shooting actions
    return [
        (MOVE, Direction.EAST),
        (MOVE, Direction.NORTH),
        (MOVE, Direction.NORTH_EAST),
        (MOVE, Direction.NORTH_WEST),
        (MOVE, Direction.SOUTH),
        (MOVE, Direction.SOUTH_EAST),
        (MOVE, Direction.SOUTH_WEST),
        (MOVE, Direction.WEST),
        (PICKUP,),
        (SHIELD,),
    ]

class MonteCarloMarkovChain(object):
    def __init__(self):
        """Creates the state -> value dict."""
        # check if file exists first. if not, initialize with zero state.
        self.q = {}

    def __del__(self):
        # save markov chain here
        print("goodbye, cruel world")

    def get_q(self, world, unit, action, enemy_units):
        # logic here for calculating rewards
        return 0

    def choose_action(self, world, unit, enemy_units):
        possible_actions = get_possible_actions(enemy_units)
        actions_to_qs = {}
        qs_to_actions = {}
        max_q = 0
        for action in possible_actions:
            q = self.get_q(world, unit, action, enemy_units)
            if q >= max_q:
                max_q = q
            actions_to_qs[action] = q
            if q not in qs_to_actions:
                qs_to_actions[q] = [action]
            else:
                qs_to_actions[q].append(action)
        best_actions = qs_to_actions[max_q]
        return random.sample(best_actions, 1)[0]

class PlayerAI:
    def __init__(self):
        # load markov graph, or create it if doesn't exist
        self.chain = MonteCarloMarkovChain()

    def do_move(self, world, enemy_units, friendly_units):
        """
        This method will get called every turn; Your glorious AI code goes here.
        :param World world: The latest state of the world.
        :param list[EnemyUnit] enemy_units: An array of all 4 units on the enemy team. Their order won't change.
        :param list[FriendlyUnit] friendly_units: An array of all 4 units on your team. Their order won't change.
        """
        # need to overlay world w/ items, players
        world = None
        for friendly_unit in friendly_units:
            # action is either MOVE, SHOOT, PICKUP, SHIELD, or STANDBY
            best_action  = self.chain.choose_action(world, friendly_unit, enemy_units)
            if best_action[0] == MOVE:
                friendly_unit.move(best_action[1])
            elif best_action[0] == SHOOT:
                friendly_unit.shoot_at(best_action[1])
            elif best_action[0] == PICKUP:
                friendly_unit.pickup_item_at_position()
            elif best_action[0] == SHIELD:
                friendly_unit.activate_shield()
