from typing import List, Dict
from Box2D import b2World, b2Vec2

from hl.io.body_def import BodyDef
from hl.io.body_parser import parse_body
from hl.utils import Vec2, Color
from hl.simulation.metrics import average_leg_x, step_length
from hl.simulation.genome.genome import Genome


JOINT_SPEED = 2


class PersonObject:
    def __init__(
        self,
        body_def: BodyDef,
        # pos: Vec2,
        world: b2World,
        color: Color,
        # angles: Dict[str, float],
    ):
        self.parts, self.joints = parse_body(
            body_def,
            world,
            color,
            # angles,
        )
        self._world = world

    def destroy(self):
        """
        Destroy the body.
        """
        for joint in self.joints.values():
            self._world.DestroyJoint(joint)
        self.joints.clear()

        for part in self.parts.values():
            self._world.DestroyBody(part.body)
        self.parts.clear()


class PersonSimulation:
    def __init__(
        self,
        body_def: BodyDef,
        gen_data: Genome,
        world: b2World,
        color: Color,
    ):

        self.genome = gen_data
        self.person = PersonObject(body_def, world, color)

        self._frames_count = 0

        # Add some metrics
        self.dead = False
        self.score = 0.0
        self.penalties = 0.0

        self.initial_head_y = self.person.parts["head"].body.position.y
        self.head_y_delta_total = 0

        self.idle_frames = 0
        self.idle_margin = 0.1
        self.idle_max_frames = 50
        # TODO: If the x position is not 0 in the body.json we may have problems
        self.idle_max_pos_x = 0

    def _update_metrics(self):
        """
        Update the person's metrics.
        """

        step = step_length(self)
        if step > 1:
            self.penalties += (step - 1) * 10.0

        self.head_y_delta_total += abs(
            self.person.parts["head"].body.position.y - self.initial_head_y
        )

        if self._frames_count > 30:
            actual_pos_x = average_leg_x(self)
            if actual_pos_x < self.idle_max_pos_x + self.idle_margin:
                self.idle_frames += 1
            else:
                self.idle_frames = 0
                self.idle_max_pos_x = actual_pos_x

    def _calculate_dead_score(self) -> float:

        avg_delta_head_y = self.head_y_delta_total / self._frames_count
        self.penalties += avg_delta_head_y * 10.0

        return average_leg_x(self) - self.penalties

    def _is_dead(self) -> bool:
        head_down = self.person.parts["head"].body.position.y < 0.7
        is_idle = self.idle_frames > self.idle_max_frames
        return head_down or is_idle

    def _update_status(self):
        """
        Updates the person's status and checks if it is dead. If it is,
        the person is removed from the world. If it is not dead, the
        person's score is updated.
        """
        if not self.dead:
            if self._is_dead():
                self.dead = True
                self.score = self._calculate_dead_score()
                self.person.destroy()
                return

            self._update_metrics()

    def step(self):
        """
        Updates the person status and applyes a movement
        """
        self._update_status()

        t = self._frames_count
        if not self.dead:
            for joint_id, value in self.genome.step(t).items():
                self.person.joints[joint_id].motorSpeed = value * JOINT_SPEED

        self._frames_count += 1
