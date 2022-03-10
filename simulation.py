from typing import List
from Box2D import b2World
import os
import pygame


from person import PersonSimulation
from world_object import WorldObject

from utils import RESORUCES_PATH

_DEFAULT_BODY_PATH = os.path.join(RESORUCES_PATH, "bodies/body1.json")


class Simulation:
    def __init__(
        self,
        bodypath: str=_DEFAULT_BODY_PATH,
        population_size: int = 60,
        syncronous_drawing: bool=False,
    ):
        self.world: b2World = None
        self.floor: WorldObject = None
        self.population: List[PersonSimulation] = None

        self.population_size = population_size
        self.bodypath = bodypath
        self.scores = None
        self._syncronous_drawing = syncronous_drawing
        self._create_world()

    def _create_world(self):
        self.world = b2World(gravity=(0, -9.8))
        self.floor = WorldObject(
            [(-50, 0.1), (50, 0.1), (50, -0.1), (-50, -0.1)],
            self.world,
            (0, 0),
            0,
            dynamic=False,
        )

    def __check_world_creation(self):
        """
        Checks if the world has been created.
        """
        if self.world is None:
            raise Exception("World has not been created yet.")

    def _create_initial_population(self):
        self.__check_world_creation()
        # Create people
        # people: List[Person] = list()
        for i in range(self.population_size):
            person = PersonSimulation()  # haha hasn't been implemented yet
            self.population.append(person)

    def _run_generation(self):
        t = 0
        clock = pygame.time.Clock()
        while not any([p.dead for p in self.population]):
            for person in self.population:
                person.update(t)
            self.world.Step(1 / fps, 2, 1)
            if self._syncronous_drawing:
                draw_world(screen, people, floor)
            t += 1

        return [people[i].score for i in range(population_size)]

    def has_converged(self, threshold: float = 0.01) -> bool:
        """
        Checks if the simulation has converged. This is done by checking if the
        average score of the last 10 generations is below a threshold.
        """
        return (
            False
            if self.scores is None
            else sum(self.scores) / len(self.scores) < threshold
        )

    def run(self):
        self._create_initial_population()
        while not self.has_converged():
            self._run_generation()
            self._breed()
