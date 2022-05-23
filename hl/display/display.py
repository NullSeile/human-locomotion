import os
import pygame
from typing import Callable, Dict, Optional, List
import multiprocessing as mp
import numpy as np
import sys
from multiprocessing.synchronize import Event
import matplotlib.pyplot as plt
from hl.io.body_def import BodyDef
from hl.simulation.genome.genome import Genome

from hl.simulation.simulation import run_a_generation
from hl.simulation.person import PersonSimulation
from hl.display.draw import draw_object, draw_person, draw_textured, draw_world
from hl.simulation.world_object import WorldObject
from hl.utils import ASSETS_PATH


class GUI_Controller:
    def __init__(
        self,
        body_def: BodyDef,
        fps: int,
        width: int = 900,
        height: int = 600,
    ):
        self.screen = pygame.display.set_mode((width, height))

        self.fps = fps
        self.body_def = body_def

        self.data_queue: Optional[mp.Queue] = None
        self.quit_flag: Optional[Event] = None

        self.center = (0, 2)

        pygame.font.init()
        self.font = pygame.font.SysFont("Comic Sans MS", 50)

        self.floor_texture = pygame.image.load(
            os.path.join(ASSETS_PATH, "imgs/floor.png")
        )

        self.clock = pygame.time.Clock()

        self.last_generation: int = 0
        self.last_genomes: Optional[List[Genome]] = None
        self.last_scores: Optional[List[float]] = None

        self.avg_history: Dict[int, float] = dict()
        self.max_history: Dict[int, float] = dict()

    def set_async_params(self, data_queue: mp.Queue, quit_flag: Event):
        self.data_queue = data_queue
        self.quit_flag = quit_flag

    def draw_loop(
        self, population: List[PersonSimulation], floor: WorldObject, fps: int
    ):
        for event in pygame.event.get():
            if (
                event.type == pygame.QUIT
                or event.type == pygame.KEYDOWN
                and event.key in [pygame.K_ESCAPE, pygame.K_q]
            ):
                pygame.quit()
                if self.quit_flag is not None:
                    self.quit_flag.set()
                sys.exit()
                return

        self.screen.fill((0, 0, 0))
        textsurface = self.font.render(
            f"Displaying Generation: {self.last_generation}", True, (255, 255, 255)
        )
        self.screen.blit(textsurface, (0, -2))

        people_x = [
            p.person.parts["torso"].body.position.x
            for p in population
            if "torso" in p.person.parts
        ]
        if people_x:
            cur_x = self.center[0]
            target_x = max(people_x)
            vel = (2 * (target_x - cur_x)) ** 3
            new_x = cur_x + vel * (1 / fps)
            self.center = (new_x, 2)

        for p in population:
            draw_person(p.person, self.screen, self.center, 2)

        draw_textured(floor, self.floor_texture, self.screen, self.center, 2)

        pygame.display.flip()
        pygame.display.update()

        plt.draw()
        plt.pause(0.001)

        self.clock.tick(fps)

    def draw_start(self, scores: Optional[List[float]], generation: int):

        self.center = (0, 2)

        if scores is not None:
            self.avg_history[generation] = np.mean(scores)
            self.max_history[generation] = np.max(scores)

            plt.cla()

            # plt.hist(scores)
            plt.plot(self.avg_history.keys(), self.avg_history.values(), label="avg")
            plt.plot(self.max_history.keys(), self.max_history.values(), label="max")
            plt.legend()

            plt.tight_layout()

    def _refresh_last_data(self):
        if self.data_queue is None:
            raise (
                RuntimeError(
                    "First set params 'data_queue', 'quit_flag', and 'simulation' using"
                    " set_async_params"
                )
            )
        if not self.data_queue.empty():
            generation, last_genomes, last_scores = self.data_queue.get()
            self.last_generation = generation
            self.last_genomes = last_genomes
            self.last_scores = last_scores
        return (
            self.last_generation,
            self.last_genomes,
            self.last_scores,
        )

    def display_async(self):
        if self.data_queue is None:
            raise (
                RuntimeError(
                    "First set the data_queue and simulation using set_async_params"
                )
            )
        self._refresh_last_data()
        display_async(
            self.body_def,
            self.fps,
            self.last_genomes,
            self.last_scores,
            self.last_generation,
            draw_start=self.draw_start,
            draw_loop=self.draw_loop,
        )


def display_async(
    body_def: BodyDef,
    fps: int,
    last_genomes: List[Genome],
    last_scores: List[float],
    generation: int,
    draw_start: Optional[Callable[[Optional[List[float]], int], None]] = None,
    draw_loop: Optional[
        Callable[[List[PersonSimulation], WorldObject, int], None]
    ] = None,
):
    if last_genomes is None:
        return

    N_ELEMENTS = 8

    if last_scores is not None:
        gs = list(zip(last_genomes, last_scores))
        gs = sorted(gs, key=lambda x: x[1], reverse=True)
        idx = np.round(np.linspace(0, len(gs) - 1, N_ELEMENTS)).astype(int)
        selected_genomes = [gs[i][0] for i in idx]
    else:
        selected_genomes = last_genomes[:N_ELEMENTS]

    run_a_generation(
        body_def,
        selected_genomes,
        fps,
        generation,
        draw_start,
        draw_loop,
        last_scores,
    )
