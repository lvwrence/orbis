from PythonClientAPI.libs.Game import PointUtils
from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.Entities import *
from PythonClientAPI.libs.Game.World import *

import random
from Q import Q


debug = True

if debug:
    # actions
    MOVE = "move"
    SHOOT = "shoot"
    PICKUP = "pickup"
    SHIELD = "shield"

    # enemies
    ALPHA = "alpha"
    BRAVO = "bravo"
    CHARLIE = "charlie"
    DELTA = "delta"

    # state features
    DIRECTION_TO_CLOSEST_CONTROL_POINT = "direction to closest control point"
else:
    # actions
    MOVE = 0
    SHOOT = 1
    PICKUP = 2
    SHIELD = 3

    # enemies
    ALPHA = 12
    BRAVO = 13
    CHARLIE = 14
    DELTA = 15

    # features
    DIRECTION_TO_CLOSEST_CONTROL_POINT = 16

def get_possible_actions():
    actions = [
        # directions
        Direction.EAST,
        Direction.NORTH,
        Direction.NORTH_EAST,
        Direction.NORTH_WEST,
        Direction.SOUTH,
        Direction.SOUTH_EAST,
        Direction.SOUTH_WEST,
        Direction.WEST,
        # shoot enemies
        ALPHA,
        BRAVO,
        CHARLIE,
        DELTA,
        # other
        PICKUP,
        SHIELD,
    ]
    random.shuffle(actions)
    return actions

def perform_action(unit, action, enemy_units):
    if action == ALPHA:
        unit.shoot_at(enemy_units[0])
    elif action == BRAVO:
        unit.shoot_at(enemy_units[1])
    elif action == CHARLIE:
        unit.shoot_at(enemy_units[2])
    elif action == DELTA:
        unit.shoot_at(enemy_units[3])
    elif action == PICKUP:
        unit.pickup_item_at_position()
    elif action == SHIELD:
        unit.activate_shield()
    else:
        direction = action
        unit.move(direction)


class PlayerAI:
    def __init__(self):
        # load markov graph, or create it if doesn't exist
        self.Q = Q()

    def _world_to_state(self, world, enemy_units, unit):
        # only return whether we're within nearest control point, and direction to it
        nearest_control_point = world.get_nearest_control_point(unit.position)
        return tuple(
            (DIRECTION_TO_CLOSEST_CONTROL_POINT, world.get_next_direction_in_path(unit.position, nearest_control_point.position)),
        )

    def _update(self, world, enemy_units, unit):
        reward = 0
        if (unit.last_pickup_result == PickupResult.PICK_UP_COMPLETE):
            reward = 100

        state = self._world_to_state(world, enemy_units, unit)
        self.Q.update(state, get_possible_actions(), reward)

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
            best_action = self.Q.choose_action(state, get_possible_actions())
            perform_action(friendly_unit, best_action, enemy_units)
