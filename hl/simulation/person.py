from typing import List, Dict
from Box2D import b2World, b2Vec2

from hl.io.body_parser import parse_body, get_body_initial_pos
from hl.utils import Vec2, Color
from hl.simulation.metrics import average_distance_person
from hl.simulation.genome.genome import Genome


class PersonObject:
    def __init__(
        self,
        body_filepath: str,
        # pos: Vec2,
        world: b2World,
        color: Color,
        # angles: Dict[str, float],
    ):
        pos = b2Vec2(get_body_initial_pos(body_filepath))

        self.parts, self.joints = parse_body(
            body_filepath,
            pos,
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
        body_filepath: str,
        gen_data: Genome,
        world: b2World,
        color: Color,
    ):

        self.genome = gen_data
        self.person = PersonObject(body_filepath, world, color)

        self._steps_count = 0

        # Add some metrics
        self.dead = False
        self.score = 0
        self.idle_score = 0
        self.idle_margin = 0.1
        self.idle_max_score = 1
        # TODO: If the x position is not 0 in the body.json we may have problems
        self.idle_max_pos_x = 0

    def _calculate_dead_score(self) -> float:
        return 1 * average_distance_person(self)

    def _update_metrics(self):
        """
        Update the person's metrics.
        """
        if self._steps_count > 30:
            actual_pos_x = average_distance_person(self)
            if actual_pos_x < self.idle_max_pos_x + self.idle_margin:
                self.idle_score += 0.1
            else:
                self.idle_score = 0
                self.idle_max_pos_x = actual_pos_x

    def _is_dead(self) -> bool:
        head_down = self.person.parts["head"].body.position.y < 0.7
        is_idle = self.idle_score > self.idle_max_score
        return head_down or is_idle

    def update_status(self):
        """
        Updates the person's status and checks if it is dead. If it is,
        the person is removed from the world. If it is not dead, the
        person's score is updated.
        """
        t = self._steps_count
        if not self.dead:
            if self._is_dead():
                self.dead = True
                self.score = self._calculate_dead_score()
                self.person.destroy()
                return True
            self._update_metrics()

    def step(self) -> bool:
        """
        Update the person's position

        Parameters
        ----------
        world : b2World
            The world in which the person is.

        Returns
        -------
        bool
            True if the person is dead, False otherwise.
        """
        t = self._steps_count
        if not self.dead:
            for joint_id, value in self.genome.step(t).items():
                self.person.joints[joint_id].motorSpeed = value

        self._steps_count += 1
        return False
