# from traceback import FrameSummary
from typing import List, Dict, Optional, Union, Tuple
import pygame

# from pygame.locals import QUIT  # type: ignore

# import sys
from Box2D import b2World, b2Vec2
import numpy as np

# from threading import Thread
import pandas as pd

from utils import RESORUCES_PATH, Color, hsv2rgb, Vec2
from object import WorldObject
from body_parser import get_joints_def, parse_body, get_random_body_angles


class MotionData:
    def __init__(
        self,
        angles: Dict[str, float],
        loop: pd.DataFrame,
        frames_per_action: int,
    ):
        """
        Parameters of the body that will be optimized during the genetic simulation.

        For now, struct to store initial position and future actions of the body.

        Parameters
        ----------
        angles : Dict[str, float]
            The angles of the body.
        loop : pd.DataFrame
            The loop of the motion.
        """
        self.angles = angles
        self.loop = loop

        #
        self.frames_per_action = frames_per_action


class BodyPartsDef:
    def __init__(
        self,
        body_filepath: str,  # filepath
        pos: Vec2,  # position
        world: b2World,  # world
        color: Color,
    ):
        if isinstance(pos, tuple):
            pos = b2Vec2(pos)

        self.body_filepath = body_filepath
        self.pos = pos
        self.world = world
        self.color = color


class BodyParts:
    def __init__(
        self,
        body_filepath: str,  # filepath
        pos: Vec2,  # position
        world: b2World,  # world
        angles: Dict[str, float] = None,
        color: Color = (255, 255, 255, 255),
    ):
        """
        Create a body from a file. The body is created at the given position
        and is attached to the given world.

        Parameters
        ----------
        body_filepath : str
            The path to the body file.
        pos : b2Vec2, or tuple of two float.
            The position of the person. The position is in the world
            coordinates. The position is the center of the person. The
            position is in the world coordinates. b2Vec2(0, 0) is the
            center of the world. b2Vec2(1, 1) is the position 1 unit
            away from the center of the world in each direction. The
            units are in meters.
        world : b2World
            The world to attach the person to.
        color : Color, optional
            The color of the person. The default is (255, 255, 255, 255).

        Returns
        -------
        None.
        """
        if isinstance(pos, tuple):
            pos = b2Vec2(pos)

        # Create Body Parts
        self.parts, self.joints = parse_body(
            body_filepath, pos, 0, world, color, angles
        )
        self._world = world

    def destroy(self):

        for joint in self.joints.values():
            self._world.DestroyJoint(joint)

        for part in self.parts.values():
            self._world.DestroyBody(part.body)
        # self.parts.clear()

        # self.joints.clear()

    def draw(self, screen: pygame.surface.Surface, center: Vec2, radius: float):
        for p in self.parts.values():
            p.draw(screen, center, radius)


class Person:
    def __init__(
        self,
        # Body definition parameters
        body_parts_def: BodyPartsDef,
        # Motion Data Struct
        motion_data: MotionData,
        #
        n_loops: int,
    ):
        """
        Create a new person. The person is created from a body file.

        """

        # Save body motion
        self.motion_data = motion_data

        # Create Body Parts
        self.parts, self.joints = parse_body(
            body_parts_def.body_filepath,
            body_parts_def.pos,
            0,
            body_parts_def.world,
            body_parts_def.color,
            self.motion_data.angles,
        )
        self.world = body_parts_def.world
        # self.body_parts = self._generate_body_parts(body_parts_def)
        # self.body_parts = BodyParts(
        #     body_parts_def.body_filepath,
        #     body_parts_def.pos,
        #     body_parts_def.world,
        #     self.motion_data.angles,
        #     body_parts_def.color,
        # )

        #
        self.frames_per_action = self.motion_data.frames_per_action
        self.frames_per_loop = (
            len(self.motion_data.loop) * motion_data.frames_per_action
        )
        self.n_loops = n_loops
        self.dead = False
        self.score = 0

    def _generate_body_parts(self, body_parts_def: BodyPartsDef) -> BodyParts:
        return BodyParts(
            body_parts_def.body_filepath,
            body_parts_def.pos,
            body_parts_def.world,
            self.motion_data.angles,
            body_parts_def.color,
        )

    def update(self, t: int) -> bool:
        """
        Update the person's position and check if it is dead. If it is,
        the person is removed from the world. If it is not dead, the
        person's score is updated.

        Parameters
        ----------
        t : int
            The current frame.
        world : b2World
            The world in which the person is.

        Returns
        -------
        bool
            True if the person is dead, False otherwise.
        """
        if not self.dead:
            if self._is_dead() or t >= self.frames_per_loop * self.n_loops:
                self.dead = True
                self.score = self._calculate_score(t)

                for j in self.joints.values():
                    self.world.DestroyJoint(j)

                for b in self.parts.values():
                    self.world.DestroyBody(b.body)

                # self.body_parts.destroy()
                return True

            if t % self.frames_per_action == 0:
                for joint_id, joint in self.joints.items():
                    loop_index = (t // self.motion_data.frames_per_action) % len(
                        self.motion_data.loop
                    )
                    joint.motorSpeed = self.motion_data.loop[loop_index][joint_id]

        return False

    def draw(self, screen: pygame.surface.Surface, center: Vec2, radius: float):
        for p in self.parts.values():
            p.draw(screen, center, radius)
        # if not self.dead:
        #     self.body_parts.draw(screen, center, radius)

    def _is_dead(self) -> bool:
        return self.parts["head"].body.position.y < 0.7

    def _calculate_score(self, t: float):
        avg_leg_x = np.average(
            [self.parts[leg].body.position.x for leg in ["leg_f", "leg_b"]]
        )
        score = max(0, avg_leg_x) + 1  # + 2 * t / self.max_frames

        return score**4
