# Global imports
from functools import partial
from multiprocessing.pool import AsyncResult
from typing import List, Dict, Optional, Tuple
from Box2D import b2World
import os
import pygame
import pandas as pd
import numpy as np
from simulation.genome_new import Genome, GenomeFactory
from tqdm import tqdm
import multiprocessing as mp

# Our imports
from simulation.person import PersonSimulation
from simulation.world_object import WorldObject
from display.draw import draw_world
from utils import ASSETS_PATH, DEFAULT_BODY_PATH, get_rgb_iris_index


class Simulation:
    def __init__(
        self,
        # Genome params
        # bodypath: str = _DEFAULT_BODY_PATH,
        genome_factory: GenomeFactory,
        # Drawing params
        syncronous_drawing: bool = False,
        screen_to_draw: Optional[pygame.surface.Surface] = None,
        # # Simulation params
        fps: int = 30,
        # population_size: int = 60,
        population_per_process: int = 50,
        n_processes: int = 8,
        # loop_time: int = 3,  # In seconds, how much does the loop lasts
        frames_per_step: int = 5,
    ):
        self.genome_factory = genome_factory

        self.population_per_process = population_per_process
        self.n_processes = n_processes

        self._syncronous_drawing = syncronous_drawing
        if self._syncronous_drawing and screen_to_draw is None:
            raise Exception(
                "Screen must be given if syncronous drawing is used. (using"
                " screen_to_draw)"
            )
        self._screen = screen_to_draw
        self._fps = fps
        self.frames_per_step = frames_per_step

        self.total_population = self.population_per_process * self.n_processes

    def _create_world(self) -> Tuple[b2World, WorldObject]:
        world = b2World(gravity=(0, -9.8))
        floor = WorldObject(
            [(-50, 0.1), (50, 0.1), (50, -0.1), (-50, -0.1)],
            world,
            (0, 0),
            0,
            dynamic=False,
        )
        return world, floor

    def _create_initial_genomes(self) -> List[Genome]:
        genomes: List[Genome] = []
        for i in range(self.total_population):
            genomes.append(self.genome_factory.get_random_genome())

        return genomes

    def _create_population_from_genomes(
        self, genomes: List[Genome], world: b2World
    ) -> List[PersonSimulation]:
        population: List[PersonSimulation] = []
        for genome in genomes:
            person = PersonSimulation(
                self.genome_factory.body_path,
                genome,
                world,
                (255, 255, 255, 255),
            )
            population.append(person)

        return population

    def _run_generation(
        self, genomes: List[Genome], scores_ret: Optional[List[float]] = None
    ) -> List[float]:
        t = 0

        world, floor = self._create_world()

        population = self._create_population_from_genomes(genomes, world)

        while not all([p.dead for p in population]):

            world.Step(1 / self._fps, 2, 1)
            if self._syncronous_drawing:
                draw_world(self._screen, population, floor)
            if t % self.frames_per_step == 0:
                for person in population:
                    person.step()
            for person in population:
                person.update_status()
            t += 1

        return [p.score for p in population]

    def _breed(self, genomes: List[Genome], scores: List[float]) -> List[Genome]:
        """
        Breed the population.
        """
        print("Max score:" + str(max(scores)))
        distr: List[float] = list(np.array(scores) / sum(scores))

        new_genomes: List[Genome] = []
        for i in tqdm(range(self.total_population), desc="Breeding  "):

            # genome = self.genome_factory.old_get_genome_from_breed(genomes, distr)
            genome = self.genome_factory.get_genome_from_breed(genomes, distr)

            new_genomes.append(genome)

        return new_genomes

    def run(self):
        genomes = self._create_initial_genomes()

        pool = mp.Pool(self.n_processes)
        returns: List[AsyncResult] = []
        for n in range(self.n_processes):

            sli = slice(
                self.population_per_process * n, self.population_per_process * (n + 1)
            )
            returns.append(
                pool.apply_async(
                    self._run_generation,
                    args=[genomes[sli]],
                )
            )

        pool.close()
        pool.join()

        print([p.get() for p in returns])
