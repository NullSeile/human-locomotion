import json
from typing import Dict, Tuple
from object import Object
from Box2D import b2World, b2RevoluteJoint, b2RevoluteJointDef, b2Vec2

from utils import Color, deg2rad


BODY_SCALE = 21


def parse_body(
    path: str, pos: b2Vec2, angle: float, world: b2World, color: Color
) -> Tuple[Dict[str, Object], Dict[str, b2RevoluteJoint]]:
    bodyDef: dict = json.load(open(path))
    root_id = bodyDef["root"]
    body = bodyDef["body"]

    col_mult = 0.7
    second_color = (
        color[0] * col_mult,
        color[1] * col_mult,
        color[2] * col_mult,
        color[3],
    )

    objs: Dict[str, Object] = dict()
    joints: Dict[str, b2RevoluteJoint] = dict()
    for key, part in body.items():
        obj = Object(
            vertices=[b2Vec2(v) / BODY_SCALE for v in part["vertices"]],
            world=world,
            color=color if part["color"] == 0 else second_color,
            categoryBits=0x0002,
            maskBits=0xFFFF & ~0x0002,
        )
        objs[key] = obj

    # For recursively initializing the position of the body parts
    def init_part(part_id: str, pos: b2Vec2, angle: float):
        objs[part_id].body.position = pos

        partDef = body[part_id]
        if "children" in partDef:
            for child_id, data in partDef["children"].items():

                jointDef = b2RevoluteJointDef()

                jointDef.bodyA = objs[part_id].body
                jointDef.bodyB = objs[child_id].body
                jointDef.localAnchorA = b2Vec2(data["anchorA"]) / BODY_SCALE
                jointDef.localAnchorB = b2Vec2(data["anchorB"]) / BODY_SCALE
                jointDef.enableMotor = True
                jointDef.maxMotorTorque = 50

                if "angle" in data:
                    jointDef.enableLimit = True
                    jointDef.lowerAngle = deg2rad(data["angle"]["min"])
                    jointDef.upperAngle = deg2rad(data["angle"]["max"])

                joints[f"{part_id}-{child_id}"] = world.CreateJoint(jointDef)

                init_part(
                    part_id=child_id,
                    pos=pos + jointDef.localAnchorA - jointDef.localAnchorB,
                    angle=angle,
                )

    init_part(root_id, pos, angle)

    return objs, joints


if __name__ == "__main__":
    from utils import RESORUCES_PATH
    import pygame
    from pygame.locals import QUIT
    import sys

    world = b2World(gravity=(0, -9.8))

    width = 900
    height = 600
    screen = pygame.display.set_mode((width, height))

    parts, joints = parse_body(
        RESORUCES_PATH + "bodies/body1.json",
        b2Vec2(0, 2),
        0,
        world,
        (255, 255, 255, 255),
    )

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
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))

        world.Step(1 / fps, 6, 3)

        for b in parts.values():
            b.draw(screen, (0, 2), 2)

        pygame.display.flip()
        pygame.display.update()

        clock.tick(fps) / 1000
