import pygame
import sys

from pygame.locals import QUIT  # type: ignore

from person import PersonObject
from utils import Vec2


def draw_person(
    person: PersonObject, screen: pygame.surface.Surface, center: Vec2, radius: float
):
    for p in person.parts.values():
        p.draw(screen, center, radius)


def draw_world(screen, people, floor):
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((0, 0, 0))

    for p in people:
        draw_person(p.person, screen, (2, 2), 2)

    floor.draw(screen, (2, 2), 2)

    pygame.display.flip()
    pygame.display.update()
