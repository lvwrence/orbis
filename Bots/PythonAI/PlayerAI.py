from PythonClientAPI.libs.Game import PointUtils
from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.Entities import *
from PythonClientAPI.libs.Game.World import *

import random
from collections import defaultdict
from Q import Q

DIRECTIONS = [
    Direction.EAST,
    Direction.NORTH,
    Direction.NORTH_EAST,
    Direction.NORTH_WEST,
    Direction.SOUTH,
    Direction.SOUTH_EAST,
    Direction.SOUTH_WEST,
    Direction.WEST,
]

# actions
MOVE_TO_CONTROL_POINT = "move to control point"
MOVE_TO_PICKUP = "move to pickup"
SHOOT_ENEMY = "shoot enemy"
PICKUP = "pickup"
SHIELD = "shield"

# state features
# (normalized) distance to the closest control point not currently controlled by us
DISTANCE_TO_CLOSEST_CONTROL_POINT = "distance to closest control point"
DISTANCE_TO_CLOSEST_PICKUP = "distance to closest pickup"
CAN_SHOOT_ENEMY = "can shoot enemy"

def get_possible_actions(world, unit, enemy_units):
    actions = []
    uncontrolled_control_points = [c for c in world.control_points if c.controlling_team != unit.team]
    if uncontrolled_control_points:
        actions.append(MOVE_TO_CONTROL_POINT)
    if world.pickups:
        actions.append(MOVE_TO_PICKUP)
    if unit.check_shield_activation() == ActivateShieldResult.SHIELD_ACTIVATION_VALID:
        actions.append(SHIELD)

    if any(unit.check_shot_against_enemy(enemy) == ShotResult.CAN_HIT_ENEMY for enemy in enemy_units):
        return [SHOOT_ENEMY]

    if unit.check_pickup_result() == PickupResult.PICK_UP_VALID:
        return [PICKUP]

    if not actions:
        # put a list of valid directions we can move to
        return [direction for direction in DIRECTIONS if unit.check_move_in_direction() == MoveResult.MOVE_VALID]

    random.shuffle(actions)
    return actions

def perform_action(world, unit, action, enemy_units):
    if action == MOVE_TO_CONTROL_POINT:
        # find nearest uncontrolled control point and move to it
        uncontrolled_control_points = [c for c in world.control_points if c.controlling_team != unit.team]
        closest_control_point = min(uncontrolled_control_points, key=lambda c: world.get_path_length(unit.position, c.position))
        direction = world.get_next_direction_in_path(unit.position, closest_control_point.position)
        unit.move(direction)
    elif action == MOVE_TO_PICKUP:
        # find nearest pickup and move to it
        closest_pickup = min(world.pickups, key=lambda p: world.get_path_length(unit.position, p.position))
        direction = world.get_next_direction_in_path(unit.position, closest_pickup.position)
        unit.move(direction)
    elif action == SHOOT_ENEMY:
        enemy = next((enemy for enemy in enemy_units if unit.check_shot_against_enemy(enemy) == ShotResult.CAN_HIT_ENEMY), None)
        unit.shoot_at(enemy)
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
        if uncontrolled_control_points:
            closest_control_point = min(uncontrolled_control_points, key=lambda c: world.get_path_length(unit.position, c.position))
            distance_to_closest_control_point = world.get_path_length(unit.position, closest_control_point.position)
        else:
            distance_to_closest_control_point = float('inf')

        if world.pickups:
            closest_pickup = min(world.pickups, key=lambda p: world.get_path_length(unit.position, p.position))
            distance_to_closest_pickup = world.get_path_length(unit.position, closest_pickup.position)
        else:
            distance_to_closest_pickup = float('inf')

        can_shoot_enemy = any(unit.check_shot_against_enemy(enemy) == ShotResult.CAN_HIT_ENEMY for enemy in enemy_units)
        return ((DISTANCE_TO_CLOSEST_CONTROL_POINT, distance_to_closest_control_point),
                (DISTANCE_TO_CLOSEST_PICKUP, distance_to_closest_pickup),
                (CAN_SHOOT_ENEMY, can_shoot_enemy),)

    def _update(self, world, enemy_units, unit):
        reward = 0
        if (unit.last_pickup_result == PickupResult.PICK_UP_COMPLETE):
            reward += 100

        captured_control_points = self.units_to_cp[unit.call_sign]
        current_control_point = next((c.name for c in world.control_points if PointUtils.chebyshev_distance(c.position, unit.position) <= 1), None)
        if current_control_point and current_control_point not in captured_control_points:
            self.units_to_cp[unit.call_sign].add(current_control_point)
            reward += 1000

        if (unit.last_shot_result == ShotResult.HIT_ENEMY):
            reward += unit.current_weapon_type.get_damage() * 250

        last_turn_shooters = unit.get_last_turn_shooters()
        if (last_turn_shooters):
            reward -= sum(shooter.current_weapon_type.get_damage() * 10 for shooter in last_turn_shooters)

        state = self._world_to_state(world, enemy_units, unit)
        self.Q.update(state, get_possible_actions(world, unit, enemy_units), reward)

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
            best_action = self.Q.choose_action(state, get_possible_actions(world, friendly_unit, enemy_units))
            perform_action(world, friendly_unit, best_action, enemy_units)
