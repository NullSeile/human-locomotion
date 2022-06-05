import argparse
import os
import sys
from typing import Dict, List, Tuple
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider
import numpy as np

from hl.io.body_def import BodyDef
from hl.simulation.person import PersonSimulation
from hl.simulation.world_object import WorldObject
from hl.utils import ASSETS_PATH, DEFAULT_BODY_PATH, load_class_from_file, rad2deg
from hl.simulation.genome.sine_genome_symetric_v3 import SineGenome
from hl.simulation.simulation import run_a_generation

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str)
args = parser.parse_args()


genome: SineGenome = load_class_from_file(args.file)


def get_maluc(n: int = 1) -> Tuple[List[float], List[float]]:

    maluc = [
        (0, 20),
        (5.8655978438983, 17.733205703501),
        (11.3467495011769, 13.8851950721069),
        (15.1835556612719, 11.4801884274855),
        (19.2944194042308, 7.1511764671671),
        (23.6793407300536, 1.3791605200759),
        (28.0642620558765, -3.4308527691668),
        (32.4491833816993, -8.0003653939473),
        (36.5600471246582, -12.81037868319),
        (40.1227957018893, -16.4178886501221),
        (44.5077170277121, -20.2658992815162),
        (50.1258974764226, -21.2279019393647),
        (54.5108188022455, -18.5823946302813),
        (58.6216825452044, -13.0508793476522),
        (61.6363159567076, -8.2408660584095),
        (64.9250, -1.0258),
        (68.8988, 5.7081),
        (73.1467, 13.8851),
        (76.8465, 18.6952),
        (80.6833, 24.4672),
        (84.5201, 27.3532),
        (88.9050, 26.8722),
        (93.2899, 24.9482),
        (96.5786, 22.7837),
        (100, 20),
    ]

    X = list()
    Y = list()
    for i in range(n):
        for x, y in maluc:
            X.append(x + i * 100)
            Y.append(y)

    return X, Y


def get_genoll(n: int = 1) -> Tuple[List[float], List[float]]:

    genoll = [
        (0, 11),
        (1.9489, 14.0296),
        (3.8698, 16.1751),
        (6.0304, 17.844),
        (8.4183, 18.9566),
        (10.3514, 19.5129),
        (12.1708, 18.6784),
        (13.8765, 17.844),
        (15.6959, 16.1751),
        (17.7427, 13.3935),
        (19.3347, 10.8902),
        (20.813, 8.3868),
        (22.2912, 5.8834),
        (23.9969, 3.1019),
        (25.7026, 0.5985),
        (27.4083, -1.0704),
        (29.3414, -3.5738),
        (31.2745, -5.799),
        (33.3213, -8.0242),
        (35.027, -9.415),
        (37.1876, -10.2494),
        (39.3481, -10.8057),
        (41.2812, -10.5276),
        (43.4417, -9.9713),
        (45.8297, -8.3024),
        (47.9902, -5.799),
        (49.5822, -3.2956),
        (51.2879, 0.3204),
        (52.9936, 4.4927),
        (54.6992, 9.4994),
        (56.0638, 13.3935),
        (57.4283, 18.1221),
        (58.6792, 22.5726),
        (59.8163, 27.3012),
        (61.2946, 32.3079),
        (62.5454, 38.1491),
        (64.1374, 43.7121),
        (65.9568, 49.2752),
        (67.6625, 54.2819),
        (69.3681, 58.7324),
        (71.3012, 62.0702),
        (73.1206, 64.8517),
        (75.736, 66.5206),
        (78.0103, 65.9643),
        (80.1708, 64.0173),
        (81.8765, 61.7921),
        (83.3548, 59.0105),
        (84.6056, 55.6727),
        (85.7427, 51.7786),
        (86.9935, 46.4937),
        (88.1307, 41.2088),
        (89.2678, 35.6457),
        (90.4049, 30.9171),
        (91.6558, 24.7978),
        (92.9066, 19.5129),
        (94.6123, 14.5061),
        (95.8631, 11.4465),
        (97.9399, 9.6535),
        (100, 11),
    ]

    X = list()
    Y = list()
    for i in range(n):
        for x, y in genoll:
            X.append(x + i * 100)
            Y.append(y)

    return X, Y


def get_turmell(n: int = 1) -> Tuple[List[float], List[float]]:

    turmell = [
        (0, 1.5128),
        (1.7701, 1.8119),
        (3.2891, 0.4659),
        (4.9248, -1.1792),
        (6.5606, -3.1234),
        (8.1964, -4.619),
        (9.8321, -5.965),
        (11.5847, -6.7128),
        (13.4542, -7.7597),
        (15.3236, -8.8065),
        (17.1931, -9.2552),
        (19.1794, -9.4048),
        (21.3993, -9.1057),
        (23.2688, -8.657),
        (25.0214, -8.3579),
        (27.1245, -8.5074),
        (29.2276, -8.9561),
        (31.3308, -9.5543),
        (33.4339, -10.1525),
        (35.8875, -11.1994),
        (37.757, -12.0968),
        (39.6264, -13.1437),
        (41.2622, -14.041),
        (43.1316, -15.5365),
        (44.6506, -17.1816),
        (45.9358, -18.9763),
        (47.5716, -20.771),
        (49.0905, -22.4161),
        (51.1936, -23.463),
        (53.0631, -22.7152),
        (55.1662, -20.9205),
        (56.802, -17.9294),
        (57.9704, -14.9383),
        (59.2556, -12.0968),
        (60.424, -8.657),
        (61.4756, -5.965),
        (62.5271, -3.5721),
        (63.6955, -1.1792),
        (65.3313, 0.4659),
        (67.3176, 1.2137),
        (69.4207, 0.3163),
        (71.407, -0.581),
        (73.8607, -0.8801),
        (76.0806, -0.7306),
        (77.9501, -0.8801),
        (79.9364, -1.4783),
        (81.689, -2.8243),
        (83.2079, -4.4694),
        (84.61, -6.4137),
        (85.8952, -8.3579),
        (87.6478, -9.5543),
        (89.5173, -10.3021),
        (91.3867, -10.9003),
        (93.1393, -10.9003),
        (94.8919, -10.6012),
        (96.8782, -9.2552),
        (98.514, -7.6101),
        (100.0, -5.5163),
    ]

    X = list()
    Y = list()
    for i in range(n):
        for x, y in turmell:
            X.append(x + i * 100)
            Y.append(y)

    return X, Y


body_def = BodyDef(DEFAULT_BODY_PATH)

data: Dict[str, List[float]] = {k: [] for k in body_def.joints.keys()}
data1: List[float] = list()

xl: List[float] = list()
maluc_yl: List[float] = list()
genoll_yl: List[float] = list()
turmell_yl: List[float] = list()
i = 0.0


def loop(population: List[PersonSimulation], floor: WorldObject, fps: int):

    global i

    p = population[0]
    if not p.dead:
        xl.append(i)
        maluc_yl.append(rad2deg(p.person.joints["torso-thigh_f"].angle))
        genoll_yl.append(rad2deg(p.person.joints["thigh_f-leg_f"].angle))
        turmell_yl.append(rad2deg(p.person.joints["leg_f-foot_f"].angle))

    #     data1.append(rad2deg(p.person.parts["torso"].body.angle))
    # for joint_id, joint in p.person.joints.items():
    # data[joint_id].append(rad2deg(joint.GetReactionTorque(1 / 30)))
    # data1[joint_id].append(rad2deg(joint.GetReactionTorque(30)))
    # data[joint_id].append(rad2deg(joint.angle))

    i += 1


run_a_generation(
    body_def=body_def,
    genomes=[genome],
    fps=30,
    generation=0,
    draw_loop=loop,
    color_function=lambda i, n: (255, 255, 255, 255),
)

x = np.array(xl)


cicles = 3


fig, ax = plt.subplots(3)
plt.subplots_adjust(bottom=0.2)

r_min = int(np.argmax(x >= 0))
r_max = int(np.argmax(x >= cicles * 100))
sli = slice(r_min, r_max)

print(max(get_maluc()[1]))

ax[0].plot(*get_maluc(cicles))
(maluc,) = ax[0].plot(x[sli], maluc_yl[sli])

ax[1].plot(*get_genoll(cicles))
(genoll,) = ax[1].plot(x[sli], genoll_yl[sli])

ax[2].plot(*get_turmell(cicles))
(turmell,) = ax[2].plot(x[sli], turmell_yl[sli])

axfreq = plt.axes([0.25, 0.1, 0.65, 0.03])
axphase = plt.axes([0.25, 0.05, 0.65, 0.03])

freq = Slider(axfreq, "Frequency", 0, 3, 1)
phase = Slider(axphase, "Phase", -100, 100, 0)


def update(val):
    xs = freq.val * (x - phase.val)

    r_min = int(np.argmax(xs >= 0))
    r_max = int(np.argmax(xs >= cicles * 100))
    sli = slice(r_min, r_max)

    maluc.set_xdata(xs[sli])
    maluc.set_ydata(maluc_yl[sli])

    genoll.set_xdata(xs[sli])
    genoll.set_ydata(genoll_yl[sli])

    turmell.set_xdata(xs[sli])
    turmell.set_ydata(turmell_yl[sli])


freq.on_changed(update)
phase.on_changed(update)

plt.show()

# sli = slice(100, 300)

# plt.plot(x[sli], maluc_yl[sli])
# plt.plot(x[sli], genoll_yl[sli])
# plt.plot(x[sli], turmell_yl[sli])

#####
# xs = 1.75 * (x - 50)  # maluc
# # xs = 1.75 * (x - 60) # genoll
# r_min = int(np.argmax(xs >= 0))
# r_max = int(np.argmax(xs >= 100))

# xs = xs[r_min:r_max]
# ys = y[r_min:r_max]

# plt.plot(xs, ys)

# for i in range(len(xs)):
#     print(f"({xs[i]},{ys[i]:.3f})", end="")
#####

# Xl, Yl = get_maluc()
# # Xl, Yl = get_genoll()
# X = np.array(Xl)
# Y = np.array(Yl)

# plt.plot(X, Y)
# plt.plot(X + 100, Y)
# plt.plot(X - 100, Y)

# (p,) = plt.plot((1.75 * (x - 20))[:200], y[:200])

# axfreq = plt.axes([0.25, 0.15, 0.65, 0.03])
# axphase = plt.axes([0.25, 0.1, 0.65, 0.03])

# freq = Slider(axfreq, "Frequency", 0, 3, 1.75)
# phase = Slider(axphase, "Phase", -100, 100, 20)


# def update(val):
#     p.set_xdata((freq.val * (x - phase.val))[:200])


# freq.on_changed(update)
# phase.on_changed(update)

# plt.tight_layout()


# name = "Torque"

# plt.title(f"{name} Maluc")
# plt.plot(data["torso-thigh_f"])
# plt.tight_layout()
# plt.show()

# plt.title(f"{name} Genoll")
# plt.plot(data["thigh_f-leg_f"])
# plt.tight_layout()
# plt.show()

# plt.title(f"{name} Turmell")
# plt.plot(data["leg_f-foot_f"])
# plt.tight_layout()
# plt.show()
