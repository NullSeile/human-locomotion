import pygame
from typing import Tuple

RESORUCES_PATH = "./resources/"

Vec2 = Tuple[float, float]
Color = Tuple[int, int, int]

# Maps a float x, which goes from x0 to x1, to go from y0 to y1
def map(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    return y0 + ((y1 - y0) / (x1 - x0)) * (x - x0)


def to_screen_pos(
    pos: Tuple[float, float],
    center: Tuple[float, float],
    radius: float,
    screen: pygame.Surface,
) -> Tuple[int, int]:
    width = screen.get_width()
    height = screen.get_height()

    aspect = width / height

    x = map(pos[0], center[0] - radius * aspect, center[0] + radius * aspect, 0, width)
    y = map(pos[1], center[1] - radius, center[1] + radius, height, 0)

    return x, y


def div(v: Vec2, s: float) -> Vec2:
    return v[0] / s, v[1] / s


def add(v1: Vec2, v2: Vec2) -> Vec2:
    return v1[0] + v2[0], v1[1] + v2[1]


def sub(v1: Vec2, v2: Vec2) -> Vec2:
    return v1[0] - v2[0], v1[1] - v2[1]
