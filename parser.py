import json
from typing import Dict, Tuple
from physics import Object, CreateJoint
from Box2D import b2World, b2RevoluteJoint

from utils import Vec2, div

BODY_SCALE = 21

PRIMARY_COLOR = (255, 255, 255)
SECONDARY_COLOR = (200, 200, 200)


def parse_body(
    path: str, pos: Vec2, angle: float, world: b2World
) -> Tuple[Dict[str, Object], Dict[str, b2RevoluteJoint]]:
    bodyDef: dict = json.load(open(path))
    root = bodyDef["root"]

    objs = dict()
    joints = dict()
    for key, part in bodyDef["body"].items():
        obj = Object(
            vertices=[div(v, BODY_SCALE) for v in part["vertices"]],
            world=world,
            pos=pos,
            color=PRIMARY_COLOR if part["color"] == 0 else SECONDARY_COLOR,
            categoryBits=0x0002,
            maskBits=0xFFFF & ~0x0002,
        )
        objs[key] = obj

    def init_part(part: str, pos: Vec2, angle: float):
        print(part)

        # for child in objs[part]["children"]:
        #     print(child)
        # init_part(child, pos, angle)
        # if parts[part].

    init_part(root, pos, angle)
    # print(root)

    return objs, joints


if __name__ == "__main__":
    from utils import RESORUCES_PATH
    import pygame
    import sys

    world = b2World(gravity=(0, -9.8))

    width = 900
    height = 600
    screen = pygame.display.set_mode((width, height))

    parts, joints = parse_body(RESORUCES_PATH + "bodies/body1.json", (0, 2), 0, world)

    parts["_floor"] = Object(
        [(-50, 0.1), (50, 0.1), (50, -0.1), (-50, -0.1)],
        world,
        (0, 0),
        0,
        dynamic=False,
    )

    fps = 60
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))

        world.Step(1 / fps, 6, 3)

        for b in parts.values():
            b.draw(screen, (0, 2), 2)

        pygame.display.flip()
        pygame.display.update()

        clock.tick(fps) / 1000
