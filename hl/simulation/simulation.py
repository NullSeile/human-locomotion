# Global imports
from multiprocessing.pool import AsyncResult
import pickle
from typing import Any, List, Optional, Tuple
from Box2D import b2World

import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""

import pygame
import numpy as np
from tqdm import tqdm
import multiprocessing as mp

# Our imports
from hl.simulation.genome.genome import Genome, GenomeBreeder
from hl.simulation.person import PersonSimulation
from hl.simulation.world_object import WorldObject

from hl.display.draw import draw_world
from hl.utils import ASSETS_PATH, get_rgb_iris_index


class Simulation:
    def __init__(
        self,
        # Genome params
        genome_breeder: GenomeBreeder,
        # Simulation params
        fps: int = 30,
        population_size: int = 64,
        parallel: bool = True,
        n_processes: int = 4,
        frames_per_step: int = 5,
        # Drawing
        screen_to_draw: Optional[pygame.surface.Surface] = None,
    ):
        self.genome_breeder = genome_breeder

        self.parallel = parallel
        self.population_size = population_size
        self.n_processes = n_processes

        if parallel:
            if population_size % n_processes != 0:
                raise ValueError(
                    "In parallel simulation, the population_size must be divisible by"
                    " the number of processes."
                )

            if screen_to_draw is not None:
                raise ValueError("Drawing is not supported yet in parallel simulation")

        self.screen_to_draw = screen_to_draw

        self._fps = fps
        self.frames_per_step = frames_per_step

        self.prev_best_score = 0.0

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
        for i in range(self.population_size):
            genomes.append(self.genome_breeder.get_random_genome())

        return genomes

    def _create_population_from_genomes(
        self, genomes: List[Genome], world: b2World
    ) -> List[PersonSimulation]:
        population: List[PersonSimulation] = []
        for i, genome in enumerate(genomes):
            person = PersonSimulation(
                self.genome_breeder.body_def,
                genome,
                world,
                get_rgb_iris_index(i, len(genomes)),
            )
            population.append(person)

        return population

    def _run_generation(self, genomes: List[Genome]) -> List[float]:

        world, floor = self._create_world()
        population = self._create_population_from_genomes(genomes, world)

        t = 0
        clock = pygame.time.Clock()
        while not all([p.dead for p in population]):
            # Step in the world
            world.Step(1 / self._fps, 6 * 10, 3 * 10)

            # If enough time has passed, update the population
            if t % self.frames_per_step == 0:
                for person in population:
                    person.step()

            # Update metrics of population
            for person in population:
                person.update_status()

            # Draw the world
            if self.screen_to_draw is not None and not self.parallel:
                draw_world(self.screen_to_draw, population, floor)
                clock.tick(self._fps)

            t += 1

        return [p.score for p in population]

    def _run_generation_parallel(self, genomes: List[Genome]) -> List[float]:
        pool = mp.Pool(self.n_processes)
        returns: List[AsyncResult] = []

        population_per_process = self.population_size // self.n_processes

        for n in range(self.n_processes):
            sli = slice(
                population_per_process * n,
                population_per_process * (n + 1),
            )
            returns.append(
                pool.apply_async(
                    self._run_generation,
                    args=[genomes[sli]],
                )
            )

        pool.close()

        pool.join()

        scores: List[float] = []
        for p in returns:
            scores += p.get()

        return scores

    def _breed(self, genomes: List[Genome], scores: List[float]) -> List[Genome]:
        """
        Breed the population.
        """
        print(f"score: avg={np.mean(scores):.5f}, max={max(scores):.5f}")
        distr: List[float] = list(np.array(scores) / sum(scores))

        best_index = np.argmax(scores)
        best_score = scores[best_index]

        if best_score > self.prev_best_score:
            self.prev_best_score = best_score
            with open(
                os.path.join(ASSETS_PATH, f"checkpoints/{best_score:.4f}.nye"), "xb"
            ) as file:
                file.write(pickle.dumps(genomes[best_index]))

        new_genomes: List[Genome] = [genomes[best_index]]
        for _ in tqdm(range(self.population_size - 1), desc="Breeding  "):
            genome = self.genome_breeder.get_genome_from_breed(genomes, distr)
            new_genomes.append(genome)

        return new_genomes

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
        genomes = self._create_initial_genomes()

        while not self.has_converged():
            scores = (
                self._run_generation_parallel(genomes)
                if self.parallel
                else self._run_generation(genomes)
            )
            genomes = self._breed(genomes, scores)
