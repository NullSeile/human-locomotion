from typing import Dict, Tuple, Optional
from Box2D import b2World, b2RevoluteJoint, b2RevoluteJointDef, b2Vec2

from hl.io.body_def import BodyDef
from hl.simulation.world_object import WorldObject
from hl.utils import Color, deg2rad, rotate, Vec2


BODY_SCALE = 21


def parse_body(
    body_def: BodyDef,
    world: b2World,
    color: Color,
    angles: Optional[Dict[str, float]] = None,
) -> Tuple[Dict[str, WorldObject], Dict[str, b2RevoluteJoint]]:

    col_mult = 0.7
    second_color = (
        int(color[0] * col_mult),
        int(color[1] * col_mult),
        int(color[2] * col_mult),
        color[3],
    )

    objs: Dict[str, WorldObject] = dict()
    joints: Dict[str, b2RevoluteJoint] = dict()
    for key, part in body_def.body.items():
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

        part_def = body_def.body[part_id]
        if "children" in part_def:
            for child_id, data in part_def["children"].items():

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

    init_part(body_def.root, body_def.pos, 0)

    return objs, joints
