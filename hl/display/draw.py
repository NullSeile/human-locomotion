import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""


import pygame
from pygame import gfxdraw

from hl.simulation.world_object import WorldObject
from hl.simulation.person import PersonObject
from hl.utils import Vec2, scale


def to_screen_pos(
    pos: Vec2,
    center: Vec2,
    radius: float,
    screen,
) -> Vec2:
    width = screen.get_width()
    height = screen.get_height()

    aspect = width / height

    x = scale(
        pos[0], center[0] - radius * aspect, center[0] + radius * aspect, 0, width
    )
    y = scale(pos[1], center[1] - radius, center[1] + radius, height, 0)

    return x, y


def draw_object(
    object: WorldObject,
    screen: pygame.surface.Surface,
    center: Vec2,
    radius: float,
):
    trans = object.body.transform

    verts = [
        to_screen_pos(trans * v, center, radius, screen) for v in object.shape.vertices
    ]
    gfxdraw.filled_polygon(screen, verts, object.color)
    gfxdraw.aapolygon(screen, verts, object.color)
    pygame.draw.polygon(screen, color=(120, 120, 120), points=verts, width=1)


def draw_textured(
    object: WorldObject,
    texture: pygame.surface.Surface,
    screen: pygame.surface.Surface,
    center: Vec2,
    radius: float,
):
    trans = object.body.transform

    verts = [
        to_screen_pos(trans * v, center, radius, screen) for v in object.shape.vertices
    ]

    width = abs(verts[0][0] - verts[2][0])
    height = abs(verts[0][1] - verts[2][1])
    topleft = verts[2]

    texture = pygame.transform.scale(texture, (width, height))

    screen.blit(texture, topleft)
    pygame.draw.polygon(screen, color=(120, 120, 120), points=verts, width=1)


def draw_person(
    person: PersonObject, screen: pygame.surface.Surface, center: Vec2, radius: float
):
    for p in person.parts.values():
        draw_object(p, screen, center, radius)


def draw_world(screen, people, floor):
    for p in people:
        draw_person(p.person, screen, (2, 2), 2)

    draw_object(floor, screen, (2, 2), 2)
