import math
import pygame
from typing import Tuple
from colorsys import hsv_to_rgb

RESORUCES_PATH = "./resources/"

Color = Tuple[int, int, int, int]

# Maps a float x, which goes from x0 to x1, to go from y0 to y1
def homo(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
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

    x = homo(pos[0], center[0] - radius * aspect, center[0] + radius * aspect, 0, width)
    y = homo(pos[1], center[1] - radius, center[1] + radius, height, 0)

    return x, y


def deg2rad(deg: float) -> float:
    return deg * math.pi / 180


def hsv2rgb(h: float, s: float, v: float, a: float = 1):
    hsv = hsv_to_rgb(h, s, v)

    return (hsv[0] * 255, hsv[1] * 255, hsv[2] * 255, a * 255)
