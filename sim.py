from typing import Tuple, Dict
import sys
import pygame
from pygame import gfxdraw
from pygame.locals import QUIT
from Box2D import b2World, b2PolygonShape, b2FixtureDef, b2Body, b2RevoluteJoint, b2WeldJoint, b2_dynamicBody, b2_staticBody

from math import pi

from utils import to_screen_pos

Vec2 = Tuple[float, float]

class BodyPart:
	def __init__(self, vertices, pos: Vec2, angle: float, world: b2World, color: Tuple[int, int, int] = (255, 255, 255),
				 dynamic: bool = True, categoryBits = None):
		self.color = color
		
		self.shape = b2PolygonShape()
		self.shape.vertices = vertices
		
		maskBits = None
		if categoryBits is None:
			categoryBits = 0x0001 if dynamic else 0x0002
			maskBits = 0xFFFF & ~0x0001 if dynamic else 0xFFFF
		else:
			maskBits = 0xFFFF
		
		self.fixture = b2FixtureDef(
			shape=self.shape,
			density=1,
			friction=0.5,
			categoryBits=categoryBits,
			maskBits=maskBits
		)
		self.body: b2Body = world.CreateBody(
			type=b2_dynamicBody if dynamic else b2_staticBody,
			fixtures=self.fixture,
			position=pos,
			angle=angle,
			# angularDamping=10,
			# linearDamping=1
		)
		
	def draw(self, screen: pygame.Surface, center: Vec2, radius: float):
		trans = self.body.transform
		
		path = [to_screen_pos(trans * v, center, radius, screen) for v in self.shape.vertices]
		gfxdraw.filled_polygon(screen, path, self.color)
		gfxdraw.aapolygon(screen, path, self.color)
		pygame.draw.polygon(screen, color=(120, 120, 120), points=path, width=1)

def CreateJoint(bodyA: BodyPart, bodyB: BodyPart, anchorA: Vec2, anchorB: Vec2, world: b2World, lowerAngle: float = None, upperAngle: float = None, refAngle: float = 0) -> b2RevoluteJoint:
	return world.CreateRevoluteJoint(
		bodyA=bodyA.body,
		bodyB=bodyB.body,
		localAnchorA=anchorA,
		localAnchorB=anchorB,
		enableMotor=True,
		maxMotorTorque=500,
		# enableLimit=(lowerAngle is not None) and (upperAngle is not None),
		# lowerAngle=lowerAngle,
		# upperAngle=upperAngle,
		referenceAngle=refAngle
	)

def CreateWeld(bodyA: BodyPart, bodyB: BodyPart, anchorA: Vec2, anchorB: Vec2, world: b2World) -> b2WeldJoint:
	return world.CreateWeldJoint(
		bodyA=bodyA.body,
		bodyB=bodyB.body,
		localAnchorA=anchorA,
		localAnchorB=anchorB
	)

if __name__ == "__main__":
	
	world = b2World(gravity=(0, -9.8))
	
	width = 900
	height = 600
	screen = pygame.display.set_mode((width, height))
	
	pos = (0, -10)
	
	PRIMARY_COLOR = (255, 255, 255)
	SECONDARY_COLOR = (200, 200, 200)
	parts: Dict[str, BodyPart] = {
		"floor": BodyPart([(-50, 0.1), (50, 0.1), (50, -0.1), (-50, -0.1)], (0, -30), 0, world, dynamic=False),
		
		"biceps_b": BodyPart([(1.5,4.5), (-1.5,4.5), (-1.5,-4.5), (1.5,-4.5)], pos, 0, world, color=SECONDARY_COLOR),
		"arm_b": BodyPart([(1,4), (-1,4), (-1,-4), (1,-4)], pos, 0, world, color=SECONDARY_COLOR),
		
		"thigh_b": BodyPart([(2,4.5), (-2,4.5), (-2,-4.5), (2,-4.5)], pos, 0, world, color=SECONDARY_COLOR),
		"leg_b": BodyPart([(1,-1.5), (1,8.5), (-1,8.5), (-1,-1.5)], pos, 0, world, color=SECONDARY_COLOR),
		
		"head": BodyPart([(2.5,2.5), (-2.5,2.5), (-2.5,-2.5), (2.5,-2.5)], pos, 0, world, color=PRIMARY_COLOR),
		"torso": BodyPart([(3,6), (-3,6), (-3,-6), (3,-6)], pos, 0, world, color=PRIMARY_COLOR),
		
		"thigh_f": BodyPart([(2,4.5), (-2,4.5), (-2,-4.5), (2,-4.5)], pos, 0, world, color=PRIMARY_COLOR),
		"leg_f": BodyPart([(1,-1.5), (1,8.5), (-1,8.5), (-1,-1.5)], pos, 0, world, color=PRIMARY_COLOR),
		# "foot_f": BodyPart([(4,1.5),(-1,1.5),(-1,-1.5),(4,-1.5)], (0, 0), 0, world),
		
		"biceps_f": BodyPart([(1.5,4.5), (-1.5,4.5), (-1.5,-4.5), (1.5,-4.5)], pos, 0, world, color=PRIMARY_COLOR),
		"arm_f": BodyPart([(1,4), (-1,4), (-1,-4), (1,-4)], pos, 0, world, color=PRIMARY_COLOR),
		
		"projectile": BodyPart([(-1,-1), (-1,1), (1,1), (1,-1)], (20, 5), 0, world, categoryBits=0x0004)
	}

	joints: Dict[str, b2RevoluteJoint] = {
		"neck": CreateJoint(parts['torso'], parts['head'], (0, 6), (0, -2.5), world),
		
		"f_arm_1": CreateJoint(parts['torso'], parts['biceps_f'], (0, 5), (0, 4.5), world),
		"f_arm_2": CreateJoint(parts['biceps_f'], parts['arm_f'], (0, -4.5), (0, 4), world, refAngle=0.2),
		
		"b_arm_1": CreateJoint(parts['torso'], parts['biceps_b'], (0, 5), (0, 4.5), world),
		"b_arm_2": CreateJoint(parts['biceps_b'], parts['arm_b'], (0, -4.5), (0, 4), world),
		
		"f_leg_1": CreateJoint(parts['torso'], parts['thigh_f'], (0, -6), (0, 4.5), world),
		"f_leg_2": CreateJoint(parts['thigh_f'], parts['leg_f'], (0, -4.5), (0, 8.5), world),
		
		"b_leg_1": CreateJoint(parts['torso'], parts['thigh_b'], (0, -6), (0, 4.5), world),
		"b_leg_2": CreateJoint(parts['thigh_b'], parts['leg_b'], (0, -4.5), (0, 8.5), world),
	}
	
	for j in joints.values():
		j.motorEnabled=True
	
	proj = parts["projectile"]
	proj.body.ApplyLinearImpulse((-70, 20), proj.body.worldCenter, True)
	
	# joints["f_arm_1"].motorSpeed = 5
	# joints["b_arm_1"].motorSpeed = -5
	
	# parts: Dict[str, BodyPart] = {
	# 	'floor': BodyPart([(-10, 0.1), (10, 0.1), (10, -0.1), (-10, -0.1)], (0, -10), 0, world, dynamic=False),
	# 	'b1': BodyPart([(-1, -0.1), (1, -0.1), (1, 0.1), (-1, 0.1)], (0, 0), 0.8, world),
	# 	'b2': BodyPart([(-1, -0.1), (1, -0.1), (1, 0.1), (-1, 0.1)], (0, 0), 0, world),
	# 	# 'b3': BodyPart([(-1, -0.2), (1, -0.2), (1, 0.6), (-1, 0.1)], (0, 0), 0.4, world),
	# }
	#
	# CreateJoint(parts['b1'], parts['b2'], (1, 0), (-1, 0), world, 0, 0, 0.5)
	
	fps = 60
	world.Step(1 / fps, 6, 3)
	# world.Step(1 / fps, 6, 3)
	# world.Step(1 / fps, 6, 3)
	clock = pygame.time.Clock()
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
		
		screen.fill((0, 0, 0))
		
		world.Step(1 / fps, 6, 3)
		
		for b in parts.values():
			b.draw(screen, (0, 0), 30)
		
		pygame.display.flip()
		pygame.display.update()
		
		clock.tick(fps) / 1000