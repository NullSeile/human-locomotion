import json
import numpy as np
from typing import Dict

from hl.utils import Vec2


class BodyDef:
    def __init__(self, body_path: str):
        body_json = json.load(open(body_path))

        self.root: str = body_json["root"]
        self.pos: Vec2 = body_json["pos"]
        self.body: dict = body_json["body"]

        self.joints = dict()
        for part_id, part_def in self.body.items():
            if "children" in part_def:
                for child_id, joint_def in part_def["children"].items():
                    joint_id = f"{part_id}-{child_id}"

                    joint_def["bodyA"] = part_id
                    joint_def["bodyB"] = child_id

                    self.joints[joint_id] = joint_def


def get_random_body_angles(body_def: BodyDef, scale: float = 1) -> Dict[str, float]:
    angles: Dict[str, float] = dict()

    for joint_id, joint_def in body_def.joints.items():
        if "angle" in joint_def:
            if "angle" in joint_def:
                min = joint_def["angle"]["min"] * scale
                max = joint_def["angle"]["max"] * scale
                angles[joint_id] = np.random.uniform(min, max)
            else:
                angles[joint_id] = 0

    return angles
