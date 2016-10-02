from PythonClientAPI.libs.Game import PointUtils
from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.Entities import *
from PythonClientAPI.libs.Game.World import *

import random
from collections import defaultdict
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
    # (normalized) distance to the closest control point not currently controlled by us
    DISTANCE_TO_CLOSEST_CONTROL_POINT = "distance to closest control point"
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
    DISTANCE_TO_CLOSEST_CONTROL_POINT = 16
    DIRECTION_TO_CLOSEST_CONTROL_POINT = 17

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
        self.Q = Q()
        self.units_to_cp = defaultdict(set)

    def _world_to_state(self, world, enemy_units, unit):
        uncontrolled_control_points = [c for c in world.control_points if c.controlling_team != unit.team]
        closest_control_point = min(uncontrolled_control_points, key=lambda c: world.get_path_length(unit.position, c.position))
        return ((DISTANCE_TO_CLOSEST_CONTROL_POINT, world.get_path_length(unit.position, closest_control_point.position) // 5),
                (DIRECTION_TO_CLOSEST_CONTROL_POINT, world.get_next_direction_in_path(unit.position, closest_control_point.position)),
               )

    def _update(self, world, enemy_units, unit):
        reward = 0
        # if (unit.last_pickup_result == PickupResult.PICK_UP_COMPLETE):
            # reward = 100

        captured_control_points = self.units_to_cp[unit.call_sign]
        current_control_point = next((c.name for c in world.control_points if PointUtils.chebyshev_distance(c.position, unit.position) <= 1), None)
        if current_control_point and current_control_point not in captured_control_points:
            self.units_to_cp[unit.call_sign].add(current_control_point)
            reward += 1000

        # if (unit.last_move_result == MoveResult.MOVE_COMPLETED):
            # reward = 5

        # if (unit.last_shot_result == ShotResult.HIT_ENEMY):
            # reward = unit.current_weapon_type.get_damage() * 10

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
