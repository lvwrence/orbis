from PythonClientAPI.libs.Game import PointUtils
from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.Entities import *
from PythonClientAPI.libs.Game.World import *

import random
from Q import Q

MOVE = 0
SHOOT = 1
PICKUP = 2
SHIELD = 3

# IS_UNIT_WITHIN_5_SQUARES_TO_CLOSEST_POWERUP = 4
IS_UNIT_WITHIN_5_SQUARES_TO_CLOSEST_CONTROL_POINT = 5
DIRECTION_TO_CLOSEST_CONTROL_POINT = 6

def get_possible_actions(enemy_units):
    # append dem shooting actions
    actions = [
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
    ] + [
        (SHOOT, enemy_unit) for enemy_unit in enemy_units
    ]
    random.shuffle(actions)
    return actions

def perform_action(unit, action):
    if (action[0] == MOVE):
        unit.move(action[1])
    elif (action[0] == SHOOT):
        unit.shoot_at(action[1])
    elif (action[0] == PICKUP):
        unit.pickup_item_at_position()
    elif (action[0] == SHIELD):
        unit.activate_shield()


class PlayerAI:
    def __init__(self):
        # load markov graph, or create it if doesn't exist
        self.Q = Q()

    def _world_to_state(self, world, enemy_units, unit):
        # only return whether we're within nearest control point, and direction to it
        # nearest_control_point = world.get_nearest_control_point(unit.position)
        # return (
            # (DIRECTION_TO_CLOSEST_CONTROL_POINT, world.get_next_direction_in_path(unit.position, nearest_control_point.position)),
        #)
        return 0

    def _update(self, world, enemy_units, unit):
        reward = 0
        if (unit.last_pickup_result == PickupResult.PICK_UP_COMPLETE):
            reward = 100

        state = self._world_to_state(world, enemy_units, unit)
        self.Q.update(state, get_possible_actions(enemy_units), reward)

    def do_move(self, world, enemy_units, friendly_units):
        """
        This method will get called every turn; Your glorious AI code goes here.
        :param World world: The latest state of the world.
        :param list[EnemyUnit] enemy_units: An array of all 4 units on the enemy team. Their order won't change.
        :param list[FriendlyUnit] friendly_units: An array of all 4 units on your team. Their order won't change.
        """
        for friendly_unit in friendly_units:
            self._update(world, enemy_units, friendly_unit)
            state = self._world_to_state(world, enemy_units, friendly_unit)
            best_action = self.Q.choose_action(state, get_possible_actions(enemy_units))
            perform_action(friendly_unit, best_action)
