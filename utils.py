import math
import pygame
from typing import Tuple, Union
from colorsys import hsv_to_rgb
from Box2D import b2Vec2
import os

ASSETS_PATH = "./assets/"

Color = Tuple[int, int, int, int]
Vec2 = Union[b2Vec2, Tuple[float, float]]


DEFAULT_BODY_PATH = os.path.join(ASSETS_PATH, "bodies/body1.json")

# Maps a float x, which goes from x0 to x1, to go from y0 to y1
def map(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    return y0 + ((y1 - y0) / (x1 - x0)) * (x - x0)


def to_screen_pos(
    pos: Vec2,
    center: Vec2,
    radius: float,
    screen: pygame.surface.Surface,
) -> Vec2:
    width = screen.get_width()
    height = screen.get_height()

    aspect = width / height

    x = map(pos[0], center[0] - radius * aspect, center[0] + radius * aspect, 0, width)
    y = map(pos[1], center[1] - radius, center[1] + radius, height, 0)

    return b2Vec2(x, y)


def deg2rad(deg: float) -> float:
    return deg * math.pi / 180


def hsv2rgb(h: float, s: float, v: float, a: float = 1):
    hsv = hsv_to_rgb(h, s, v)

    return (hsv[0] * 255, hsv[1] * 255, hsv[2] * 255, a * 255)


def get_rgb_iris_index(index: int, max_index: int) -> Color:
    colour = hsv2rgb(index / max_index, 0.5, 0.8, 0.5)
    return colour


def rotate(v: Vec2, a: float) -> Vec2:
    if isinstance(v, tuple):
        v = b2Vec2(v)

    return b2Vec2(
        v.x * math.cos(a) - v.y * math.sin(a), v.x * math.sin(a) + v.y * math.cos(a)
    )
