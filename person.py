from typing import List, Dict
from Box2D import b2World, b2Joint, b2Vec2
import pandas as pd

from world_object import WorldObject
from body_parser import parse_body
from utils import Vec2, Color

import numpy as np

from metrics import max_distance_person


class PersonObject:
    def __init__(
        self,
        body_filepath: str,
        pos: Vec2,
        world: b2World,
        color: Color,
        angles: Dict[str, float],
    ):
        if isinstance(pos, tuple):
            pos = b2Vec2(pos)

        self.parts, self.joints = parse_body(body_filepath, pos, world, color, angles)
        self._world = world


class GeneticData:
    def __init__(
        self,
        pos: Vec2,
        actions_loop: pd.DataFrame,
        angles: Dict[str, float],
    ):
        self.pos = pos
        self.actions_loop = actions_loop
        self.angles = angles


class PersonSimulation:
    def __init__(
        self,
        body_filepath: str,
        gen_data: GeneticData,
        world: b2World,
        color: Color,
        frames_per_action: int = 5,
    ):

        self.gen_data = gen_data
        self.person = PersonObject(
            body_filepath, self.gen_data.pos, world, color, self.gen_data.angles
        )

        self._actual_index = 0
        self.dead = False
        self.score = 0
        self.frames_per_action = frames_per_action

    def _calculate_dead_score(self):
        return 1 * max_distance_person(self)

    def _calculate_intermediate_score(self):
        pass

    def step(self) -> bool:
        """
        Update the person's position and checks if it is dead. If it is,
        the person is removed from the world. If it is not dead, the
        person's score is updated.

        Parameters
        ----------
        world : b2World
            The world in which the person is.

        Returns
        -------
        bool
            True if the person is dead, False otherwise.
        """
        t = self._actual_index
        if not self.dead:
            if self._is_dead() or t >= self.frames_per_loop * self.n_loops:
                self.dead = True
                self.score = self._calculate_dead_score(t)
                self.person.destroy()
                return True
            if t % self.frames_per_action == 0:
                for joint_id, joint in self.person.joints.items():
                    loop_index = (t // self.frames_per_action) % len(
                        self.gen_data.actions_loop
                    )
                    joint.motorSpeed = self.gen_data.actions_loop[loop_index][joint_id]
            self._calculate_intermediate_score()
        self._actual_index += 1
        return False
