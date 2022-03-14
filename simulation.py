# Global imports
from typing import List, Dict, Optional
from Box2D import b2World
import os
import pygame
import pandas as pd
import numpy as np
from genome import GenomeFactory

# Our imports
from person import PersonSimulation
from world_object import WorldObject
from draw import draw_world
from utils import RESORUCES_PATH, get_rgb_iris_index


class Simulation:
    def __init__(
        self,
        # Genome params
        # bodypath: str = _DEFAULT_BODY_PATH,
        genome_factory: GenomeFactory,
        # Drawing params
        syncronous_drawing: bool = False,
        screen_to_draw: Optional[pygame.surface.Surface] = None,
        # Simulation params
        fps: int = 30,
        population_size: int = 60,
        loop_time: int = 3,  # In seconds, how much does the loop lasts
        frames_per_step: int = 5,
    ):
        self.world: b2World = None
        self.floor: WorldObject = None

        self.population: List[PersonSimulation] = []
        self.genome_params_constructor = None

        self.population_size = population_size

        self.genome_factory = genome_factory

        self.scores = None
        self._syncronous_drawing = syncronous_drawing
        if self._syncronous_drawing and screen_to_draw is None:
            raise Exception(
                "Screen must be given if syncronous drawing is used. (using"
                " screen_to_draw)"
            )
        self._screen = screen_to_draw
        self._fps = fps
        self.frames_per_step = frames_per_step

        self.generation_index = 0
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
            genetic_params = self.genome_factory.get_random_genome()
            person = PersonSimulation(
                self.genome_factory.body_path,
                genetic_params,
                self.world,
                get_rgb_iris_index(i, self.population_size),
            )  # haha hasn't been implemented yet
            self.population.append(person)

    def _run_generation(self):
        t = 0
        while not all([p.dead for p in self.population]):
            self.world.Step(1 / self._fps, 2, 1)
            if self._syncronous_drawing:
                draw_world(self._screen, self.population, self.floor)
            if t % self.frames_per_step == 0:
                for person in self.population:
                    person.step()
            for person in self.population:
                person.update_status()
            t += 1
        return [p.score for p in self.population]

    def _breed(self):
        """
        Breed the population.
        """
        scores = [p.score for p in self.population]
        distr = np.array(scores) / sum(scores)

        genomes = [p.genome for p in self.population]

        new_population: List[PersonSimulation] = []
        for i in range(self.population_size):

            # genome = self.genome_factory.old_get_genome_from_breed(genomes, distr)
            genome = self.genome_factory.get_genome_from_breed(genomes, distr)
            person = PersonSimulation(
                self.genome_factory.body_path,
                genome,
                self.world,
                get_rgb_iris_index(i, self.population_size),
            )  # haha hasn't been implemented yet

            new_population.append(person)

        self.population = new_population

    def has_converged(self, threshold: float = 0.01) -> bool:
        """
        Checks if the simulation has converged. This is done by checking if the
        average score of the last 10 generations is below a threshold.
        """
        return False
        # return (
        #     False
        #     if self.scores is None
        #     else sum(self.scores) / len(self.scores) < threshold
        # )

    def run(self):
        self._create_initial_population()
        while not self.has_converged():
            self._run_generation()
            self._breed()
            self.generation_index += 1
