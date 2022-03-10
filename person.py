from typing import List, Dict
from Box2D import b2World, b2Joint, b2Vec2
import pandas as pd

from world_object import WorldObject
from body_parser import parse_body
from utils import Vec2, Color


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
    def __init__(self, pos: Vec2, actions_loop: pd.DataFrame, angles: Dict[str, float]):
        self.pos = pos
        self.actions_loop = actions_loop
        self.angles = angles


class PersonSimulation:
    def __init__(
        self, body_filepath: str, gen_data: GeneticData, world: b2World, color: Color
    ):

        self.gen_data = gen_data

        self.person = PersonObject(
            body_filepath, self.gen_data.pos, world, color, self.gen_data.angles
        )
