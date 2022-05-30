import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""


import pygame
from pygame import gfxdraw
from Box2D import b2Transform

from hl.simulation.world_object import WorldObject
from hl.simulation.person import PersonObject
from hl.utils import Vec2, rad2deg, scale


identity = b2Transform()
identity.SetIdentity()


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


def to_screen_scale(
    size: Vec2,
    radius: float,
    screen,
) -> Vec2:
    width = screen.get_width()
    height = screen.get_height()

    aspect = width / height

    x = scale(size[0], 0, 2 * radius * aspect, 0, width)
    y = scale(size[0], 0, 2 * radius, 0, height)

    return x, y


def draw_object(
    obj: WorldObject,
    screen: pygame.surface.Surface,
    center: Vec2,
    radius: float,
):
    trans = obj.body.transform

    verts = [
        to_screen_pos(trans * v, center, radius, screen) for v in obj.shape.vertices
    ]
    gfxdraw.filled_polygon(screen, verts, obj.color)
    gfxdraw.aapolygon(screen, verts, obj.color)
    pygame.draw.polygon(screen, color=(120, 120, 120), points=verts, width=1)


def draw_textured(
    obj: WorldObject,
    texture: pygame.surface.Surface,
    screen: pygame.surface.Surface,
    center: Vec2,
    radius: float,
):
    trans = obj.body.transform

    o_verts = obj.shape.vertices
    s_verts = [to_screen_pos(v, center, radius, screen) for v in o_verts]
    verts = [to_screen_pos(trans * v, center, radius, screen) for v in o_verts]

    width = abs(s_verts[0][0] - s_verts[2][0])
    height = abs(s_verts[0][1] - s_verts[2][1])

    texture = pygame.transform.scale(texture, (width, height))

    pos = to_screen_pos(obj.body.position, center, radius, screen)
    angle = rad2deg(obj.body.angle)

    if angle != 0:
        texture.set_colorkey((0, 0, 0, 0))
        texture = pygame.transform.rotate(texture, angle)

    screen.blit(
        texture,
        (pos[0] - texture.get_width() / 2, pos[1] - texture.get_height() / 2),
    )
    pygame.draw.polygon(screen, color=(120, 120, 120), points=verts, width=1)


def draw_person(
    person: PersonObject,
    screen: pygame.surface.Surface,
    center: Vec2,
    radius: float,
):
    for p in person.parts.values():
        draw_object(p, screen, center, radius)


def draw_world(screen, people, floor):
    for p in people:
        draw_person(p.person, screen, (2, 2), 2)

    draw_object(floor, screen, (2, 2), 2)
