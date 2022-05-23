import math
import pickle

from typing import Tuple, Union
from colorsys import hsv_to_rgb
from Box2D import b2Vec2
import os
from pathlib import Path

import numpy as np

ASSETS_PATH = os.path.join(Path(__file__).parent.parent, "assets")
DEFAULT_BODY_PATH = os.path.join(ASSETS_PATH, "bodies/lil_foot.json")


Color = Tuple[int, int, int, int]
Vec2 = Tuple[float, float]


# Maps a float x, which goes from x0 to x1, to go from y0 to y1
def scale(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    try:
        return y0 + ((y1 - y0) / (x1 - x0)) * (x - x0)
    except:
        print(f"x={x}, x0={x0}, x1={x1}, y0={y0}, y1={y1}")
        raise


# Normalize array to [0, 1]
def normalize(L: np.ndarray):
    max = np.max(L)
    min = np.min(L)

    if max - min != 0:
        return (L - min) / (max - min)
    else:
        return L


def to_distr(L: np.ndarray):
    norm = normalize(L)
    return norm / np.sum(norm)


def deg2rad(deg: float) -> float:
    return deg * math.pi / 180


def hsv2rgb(h: float, s: float, v: float, a: float = 1):
    hsv = hsv_to_rgb(h, s, v)

    return (hsv[0] * 255, hsv[1] * 255, hsv[2] * 255, a * 255)


def get_rgb_iris_index(index: int, max_index: int) -> Color:
    colour = hsv2rgb(index / max_index, 0.5, 0.8, 0.5)
    return colour


def rotate(v: b2Vec2, a: float) -> b2Vec2:
    return b2Vec2(
        v.x * math.cos(a) - v.y * math.sin(a), v.x * math.sin(a) + v.y * math.cos(a)
    )


def load_class_from_file(path: str):
    return pickle.loads(open(path, "rb").read())
