import pygame
import sys

from pygame.locals import QUIT  # type: ignore


def draw_world(screen, people, floor):
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((0, 0, 0))

    for p in people:
        p.draw(screen, (2, 2), 2)

    floor.draw(screen, (2, 2), 2)

    pygame.display.flip()
    pygame.display.update()
