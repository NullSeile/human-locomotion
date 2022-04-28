# Global imports
from multiprocessing.pool import AsyncResult
from typing import Any, Callable, Dict, List, Optional, Tuple
from Box2D import b2World
import pickle

import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""

import pygame
import numpy as np
from tqdm import tqdm
import threading
import multiprocessing as mp
from multiprocessing.synchronize import Event

# Our imports
from hl.simulation.genome.genome import Genome, GenomeBreeder
from hl.simulation.person import PersonSimulation
from hl.simulation.world_object import WorldObject
from hl.io.body_def import BodyDef

from hl.utils import get_rgb_iris_index, ASSETS_PATH


def create_a_world() -> Tuple[b2World, WorldObject]:
    world = b2World(gravity=(0, -9.8))
    floor = WorldObject(
        [(-50, 0.1), (50, 0.1), (50, -0.1), (-50, -0.1)],
        world,
        (0, 0),
        0,
        dynamic=False,
    )
    return world, floor


def create_a_population(
    body_def: BodyDef, genomes: List[Genome], world: b2World
) -> List[PersonSimulation]:
    population: List[PersonSimulation] = []
    for i, genome in enumerate(genomes):
        person = PersonSimulation(
            body_def,
            genome,
            world,
            get_rgb_iris_index(i, len(genomes)),
        )
        population.append(person)

    return population


def run_a_generation(
    body_def: BodyDef,
    genomes: List[Genome],
    fps: int,
    generation: int,
    draw_start: Optional[Callable[[Optional[List[float]], int], None]] = None,
    draw_loop: Optional[Callable[[List[PersonSimulation], WorldObject], None]] = None,
    scores: Optional[List[float]] = None,
) -> List[float]:
    world, floor = create_a_world()
    population = create_a_population(body_def, genomes, world)

    if draw_start is not None:
        draw_start(scores, generation)

    t = 0
    clock = pygame.time.Clock()
    while not all([p.dead for p in population]):
        # Step in the world
        world.Step(1 / fps, 6 * 10, 3 * 10)

        # If enough time has passed, update the population
        for person in population:
            person.step()

        # Draw the world
        if draw_loop is not None:
            draw_loop(population, floor)

        t += 1
        clock.tick(fps)

    return [p.score for p in population]


import time


class SimulationQueuePutter(threading.Thread):
    def __init__(self, queue: mp.Queue, quit_flag: Event):
        super().__init__()
        self.queue = queue
        self.quit_flag = quit_flag
        self.data: Optional[Tuple[int, List[Genome], Optional[List[float]]]] = None

    def run(self):
        while not self.quit_flag.is_set():
            if self.data is not None:
                while not self.queue.empty():
                    self.queue.get()
                self.queue.put(self.data)
                self.data = None
            time.sleep(0.1)

    def add_last_genomes(
        self, generation: int, genomes: List[Genome], scores: Optional[List[float]]
    ) -> None:
        self.data = (generation, genomes, scores)


class Simulation:
    def __init__(
        self,
        # Genome params
        genome_breeder: GenomeBreeder,
        sample_genome: Optional[Genome] = None,
        # Simulation params
        fps: int = 30,
        frames_per_step: int = 5,
        population_size: int = 64,
        # Parallel parameters
        parallel: bool = True,
        n_processes: int = 4,
        n_elite_genomes: int = 4,
        quit_flag: Optional[Event] = None,
        # Drawing
        draw_start: Optional[Callable] = None,
        draw_loop: Optional[
            Callable[[List[PersonSimulation], WorldObject], None]
        ] = None,
    ):
        self.genome_breeder = genome_breeder
        self.n_elite_genomes = n_elite_genomes

        self.sample_genome = sample_genome

        self.parallel = parallel
        self.population_size = population_size
        self.n_processes = n_processes

        if self.parallel:
            if population_size % n_processes != 0:
                raise ValueError(
                    "In parallel simulation, the population_size must be divisible by"
                    " the number of processes."
                )

            if draw_start is not None or draw_loop is not None:
                raise ValueError("Drawing is not supported yet in parallel simulation")

        self.draw_start = draw_start
        self.draw_loop = draw_loop

        self.generation_count = 0

        self.prev_best_score = 0.0

        self._fps = fps
        self.frames_per_step = frames_per_step
        self.population_queue_manager: Optional[SimulationQueuePutter] = None
        self._last_genomes: Optional[List[Genome]] = None
        self._last_genomes_generation = self.generation_count
        self.quit_flag = quit_flag

    def add_parallel_params(self, queue: mp.Queue) -> None:
        assert self.quit_flag is not None
        self.population_queue_manager = SimulationQueuePutter(queue, self.quit_flag)
        threading.Thread(target=self.population_queue_manager.run).start()

    def add_last_genomes(
        self, genomes: List[Genome], scores: Optional[List[float]], skip_if_blocked=True
    ) -> None:
        """
        Add the last generation of genomes to the simulation. This
        method is thread-safe.
        """
        if self.population_queue_manager is not None:
            self.population_queue_manager.add_last_genomes(
                self.generation_count, genomes, scores
            )

    def _create_world(self) -> Tuple[b2World, WorldObject]:
        return create_a_world()

    def _create_initial_genomes(self) -> List[Genome]:
        if self.sample_genome is not None:
            return [self.sample_genome] * self.population_size
        else:
            return [
                self.genome_breeder.get_random_genome()
                for _ in range(self.population_size)
            ]

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
        return run_a_generation(
            self.genome_breeder.body_def,
            genomes,
            self._fps,
            self.generation_count,
            self.draw_start,
            self.draw_loop,
        )

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
                    run_a_generation,
                    args=[
                        self.genome_breeder.body_def,
                        genomes[sli],
                        self._fps,
                        self.generation_count,
                    ],
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
        print(f"max score: {max(scores):.3f}. avg score: {np.mean(scores):.3f}")

        # Selecting the best genomes to keep for the next generation
        gs = list(zip(genomes, scores))
        gs = sorted(gs, key=lambda x: x[1], reverse=True)
        elite_genomes = gs[: self.n_elite_genomes]

        best_index = np.argmax(scores)
        best_score = scores[best_index]
        if best_score > self.prev_best_score:
            self.prev_best_score = best_score
            with open(
                os.path.join(
                    ASSETS_PATH,
                    f"checkpoints/gen={self.generation_count}_score={best_score:.4f}.nye",
                ),
                "xb",
            ) as file:
                file.write(pickle.dumps(genomes[best_index]))

        new_genomes: List[Genome] = [e[0] for e in elite_genomes]

        # Select only the best 30% of genomes to breed
        genomes_to_breed = int(len(genomes) * 0.3)
        s_gs = gs[:genomes_to_breed]
        s_genomes = [e[0] for e in s_gs]
        s_distr = list(np.array([e[1] for e in s_gs]) / sum([e[1] for e in s_gs]))
        for _ in tqdm(
            range(self.population_size - self.n_elite_genomes), desc="Breeding  "
        ):
            genome = self.genome_breeder.get_genome_from_breed(s_genomes, s_distr)
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

    def forced_quit(self) -> bool:
        if self.quit_flag is not None:
            return self.quit_flag.is_set()

        raise ValueError("Quit flag is not set but called `forced_quit`")

    def run(
        self,
        data_queue: Optional[mp.Queue] = None,
    ) -> None:
        # Init parameters
        if data_queue is not None:
            self.add_parallel_params(data_queue)

        # Start the simulation
        genomes = self._create_initial_genomes()

        while not self.has_converged() and not self.forced_quit():
            print(f"Generation {self.generation_count}")
            scores = (
                self._run_generation_parallel(genomes)
                if self.parallel
                else self._run_generation(genomes)
            )
            self.add_last_genomes(genomes, scores)
            if self.forced_quit():
                break
            genomes = self._breed(genomes, scores)
            self.generation_count += 1
        if self.quit_flag is not None:
            self.quit_flag.set()
