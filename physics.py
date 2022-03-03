from __future__ import annotations
from typing import Tuple, Dict, List
import sys
import pygame
from pygame import gfxdraw
from pygame.locals import QUIT
from Box2D import (
    b2World,
    b2PolygonShape,
    b2FixtureDef,
    b2Body,
    b2RevoluteJoint,
    b2WeldJoint,
    b2_dynamicBody,
    b2_staticBody,
)

from utils import Vec2, Color, to_screen_pos, div


class Object:
    def __init__(
        self,
        vertices: List[Vec2],
        world: b2World,
        pos: Vec2 = (0, 0),
        angle: float = 0,
        color: Color = (255, 255, 255),
        dynamic: bool = True,
        categoryBits=0x0001,
        maskBits=0xFFFF,
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
            # angularDamping=10,
            # linearDamping=1
        )

    def draw(self, screen: pygame.Surface, center: Vec2, radius: float):
        trans = self.body.transform

        path = [
            to_screen_pos(trans * v, center, radius, screen)
            for v in self.shape.vertices
        ]
        gfxdraw.filled_polygon(screen, path, self.color)
        gfxdraw.aapolygon(screen, path, self.color)
        pygame.draw.polygon(screen, color=(120, 120, 120), points=path, width=1)


def CreateJoint(
    bodyA: Object,
    bodyB: Object,
    anchorA: Vec2,
    anchorB: Vec2,
    world: b2World,
    lowerAngle: float = None,
    upperAngle: float = None,
    refAngle: float = 0,
) -> b2RevoluteJoint:
    return world.CreateRevoluteJoint(
        bodyA=bodyA.body,
        bodyB=bodyB.body,
        localAnchorA=anchorA,
        localAnchorB=anchorB,
        enableMotor=True,
        maxMotorTorque=0.1,
        # enableLimit=(lowerAngle is not None) and (upperAngle is not None),
        # lowerAngle=lowerAngle,
        # upperAngle=upperAngle,
        # referenceAngle=refAngle
    )


def CreateWeld(
    bodyA: Object, bodyB: Object, anchorA: Vec2, anchorB: Vec2, world: b2World
) -> b2WeldJoint:
    return world.CreateWeldJoint(
        bodyA=bodyA.body, bodyB=bodyB.body, localAnchorA=anchorA, localAnchorB=anchorB
    )
