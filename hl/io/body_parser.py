import json
from typing import Dict, Tuple, Optional
from Box2D import b2World, b2RevoluteJoint, b2RevoluteJointDef, b2Vec2
import numpy as np

from hl.simulation.world_object import WorldObject
from hl.utils import Color, deg2rad, rotate, Vec2


BODY_SCALE = 21


def get_body_initial_pos(path: str) -> Vec2:
    bodyDef: dict = json.load(open(path))
    pos = bodyDef["pos"]
    return pos[0], pos[1]


def get_joints_def(path: str) -> dict:
    jonits_def = dict()
    body_def: dict = json.load(open(path))
    for part_id, part_def in body_def["body"].items():
        if "children" in part_def:
            for child_id, joint_def in part_def["children"].items():
                joint_id = f"{part_id}-{child_id}"

                joint_def["bodyA"] = part_id
                joint_def["bodyB"] = child_id

                jonits_def[joint_id] = joint_def

    return jonits_def


def parse_body(
    path: str,
    pos: Vec2,
    world: b2World,
    color: Color,
    angles: Optional[Dict[str, float]] = None,
) -> Tuple[Dict[str, WorldObject], Dict[str, b2RevoluteJoint]]:

    bodyDef: dict = json.load(open(path))
    root_id = bodyDef["root"]
    body = bodyDef["body"]

    col_mult = 0.7
    second_color = (
        int(color[0] * col_mult),
        int(color[1] * col_mult),
        int(color[2] * col_mult),
        color[3],
    )

    objs: Dict[str, WorldObject] = dict()
    joints: Dict[str, b2RevoluteJoint] = dict()
    for key, part in body.items():
        obj = WorldObject(
            vertices=[b2Vec2(v) / BODY_SCALE for v in part["vertices"]],
            world=world,
            color=color if part["color"] == 0 else second_color,
            categoryBits=0x0002,
            maskBits=0xFFFF & ~0x0002,
        )
        objs[key] = obj

    # For recursively initializing the position of the body parts
    def init_part(part_id: str, pos: Vec2, angle: float):
        objs[part_id].body.position = pos
        objs[part_id].body.angle = deg2rad(angle)

        partDef = body[part_id]
        if "children" in partDef:
            for child_id, data in partDef["children"].items():

                joint_id = f"{part_id}-{child_id}"

                jointDef = b2RevoluteJointDef()

                jointDef.bodyA = objs[part_id].body
                jointDef.bodyB = objs[child_id].body
                jointDef.localAnchorA = b2Vec2(data["anchorA"]) / BODY_SCALE
                jointDef.localAnchorB = b2Vec2(data["anchorB"]) / BODY_SCALE
                jointDef.enableMotor = True
                jointDef.maxMotorTorque = 500

                next_angle = angle
                if "angle" in data:
                    jointDef.enableLimit = True
                    min = data["angle"]["min"]
                    max = data["angle"]["max"]
                    jointDef.lowerAngle = deg2rad(min)
                    jointDef.upperAngle = deg2rad(max)
                    # print(angles)
                    if angles is not None:
                        next_angle += angles[joint_id]

                joints[joint_id] = world.CreateJoint(jointDef)

                init_part(
                    part_id=child_id,
                    pos=b2Vec2(pos)
                    + rotate(jointDef.localAnchorA, angle)
                    - rotate(jointDef.localAnchorB, next_angle),
                    angle=next_angle,
                )

    init_part(root_id, pos, 0)

    return objs, joints


def get_random_body_angles(path: str, scale: float = 1) -> Dict[str, float]:
    angles: Dict[str, float] = dict()

    joints = get_joints_def(path)
    for joint_id, joint_def in joints.items():
        if "angle" in joint_def:
            if "angle" in joint_def:
                min = joint_def["angle"]["min"] * scale
                max = joint_def["angle"]["max"] * scale
                angles[joint_id] = np.random.uniform(min, max)
            else:
                angles[joint_id] = 0

    return angles
