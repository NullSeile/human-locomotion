from __future__ import annotations
from typing import List

from Box2D import (
    b2World,
    b2PolygonShape,
    b2FixtureDef,
    b2Body,
    b2Vec2,
    b2_dynamicBody,
    b2_staticBody,
)

from utils import Color


class WorldObject:
    def __init__(
        self,
        vertices: List[b2Vec2],
        world: b2World,
        pos: b2Vec2 = (0, 0),
        angle: float = 0,
        color: Color = (255, 255, 255, 255),
        dynamic: bool = True,
        categoryBits: int = 0x0001,
        maskBits: int = 0xFFFF,
    ):
        self.color = color

        self.shape = b2PolygonShape()
        self.shape.vertices = vertices

        self.fixture = b2FixtureDef(
            shape=self.shape,
            density=1,
            friction=0.5,
            categoryBits=categoryBits,
            maskBits=maskBits,
        )
        self.body: b2Body = world.CreateBody(
            type=b2_dynamicBody if dynamic else b2_staticBody,
            fixtures=self.fixture,
            position=pos,
            angle=angle,
        )
