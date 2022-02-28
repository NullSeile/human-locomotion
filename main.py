from __future__ import annotations
import pygame
from pygame import gfxdraw
from pygame.locals import *
import sys
from typing import Tuple, List
from math import *
from Box2D import b2World, b2PolygonShape, b2CircleShape, b2FixtureDef, b2_dynamicBody, b2_staticBody, b2Body

from Vec2 import Vec2
		
class Bone:
	def __init__(self, name: str, length: float, r0: float = 0, sim: bool = True, c: List[Bone] = []):
		self.name = name
		self.length = length
		self.children = c
		self.simulate = sim
		self.pos = Vec2(0, 0)
		self.vel = Vec2(0, 0)
		self.angle = r0
		self.aVel = 0
		self.body: b2Body = None
		self.shape = b2PolygonShape()

# Maps a float x, which goes from x0 to x1, to go from y0 to y1
def map(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
	return y0 + ((y1 - y0) / (x1 - x0)) * (x - x0)

def to_screen_pos(pos: Vec2, center: Vec2, radius: float, screen: pygame.Surface) -> Tuple[int, int]:
	width = screen.get_width()
	height = screen.get_height()
	
	aspect = width / height
	
	x = map(pos.x, center.x - radius*aspect, center.x + radius*aspect, 0, width)
	y = map(pos.y, center.y - radius, center.y + radius, height, 0)
	
	return x, y

def to_screen_scale(delta: float, radius: float, screen) -> int:
	return int(map(delta, 0, 2*radius, 0, screen.get_height()))


center = Vec2(0, 0)
radius = 1.5
def draw_bone(bone: Bone, screen: pygame.Surface):
	trans = bone.body.transform
	
	if bone.length == 0:
		x, y = to_screen_pos(bone.pos, center, radius, screen)
		rad = to_screen_scale(0.02, radius, screen)
		
		gfxdraw.filled_circle(screen, int(x), int(y), rad, (255, 255, 255))
		gfxdraw.aacircle(screen, int(x), int(y), rad, (255, 255, 255))
		pygame.draw.circle(screen, color=(120, 120, 120), center=(x, y), radius=rad, width=1)
	
	else:
		path = [to_screen_pos(trans * v, center, radius, screen) for v in bone.shape.vertices]
		
		gfxdraw.filled_polygon(screen, path, (255, 255, 255))
		gfxdraw.aapolygon(screen, path, (255, 255, 255))
		pygame.draw.polygon(screen, color=(120, 120, 120), points=path, width=1)
	
	for bone_child in bone.children:
		draw_bone(bone_child, screen)


def init_bone(bone: Bone, rot: float, pos: Vec2, world: b2World):
	bone.angle += rot
	L = Vec2(cos(bone.angle), sin(bone.angle)) * bone.length
	bone.pos = pos + L * 0.5
	
	if bone.length == 0:
		bone.shape = b2CircleShape(radius=0.02)
		
		fixtureDef = b2FixtureDef(
			shape=bone.shape,
			density=1,
			friction=1,
			categoryBits=0x0020,
			# maskBits=0x001
		)
		
		bone.body = world.CreateDynamicBody(fixtures=fixtureDef, position=(bone.pos.x, bone.pos.y))
		
	else:
		height = 0.05
		bone.shape.SetAsBox(bone.length/2, height/2)
		
		fixtureDef = b2FixtureDef(
			shape=bone.shape,
			density=1,
			friction=1,
			categoryBits=0x0020,
			# maskBits=0x001
		)
		
		body_type = b2_dynamicBody if bone.simulate else b2_staticBody
		
		bone.body = world.CreateBody(
			type=body_type,
			fixtures=fixtureDef,
			position=(bone.pos.x, bone.pos.y),
			angle=bone.angle,
			angularDamping=10,
			linearDamping=1
		)

	for bone_child in bone.children:
		init_bone(bone_child, bone.angle, pos + L, world)
		
		world.CreateWeldJoint(
			bodyA=bone.body,
			bodyB=bone_child.body,
			localAnchorA=(bone.length/2, 0),
			localAnchorB=(-bone_child.length/2, 0),
			collideConnected=False
		)
	
def update_bone(bone: Bone):
	bone.pos = Vec2(bone.body.position.x, bone.body.position.y)
	bone.angle = bone.body.angle
	
	for child in bone.children:
		update_bone(child)


pelvis = \
	Bone("pelvis", 0, r0=-pi/2 + 0.2, sim=True, c=[
		Bone("femur_l", 0.5, r0=-0.4, c=[
			Bone("tibia_l", 0.4, r0=0.2)
		]),
		Bone("femur_r", 0.5, r0=0.5, c=[
			Bone("tibia_r", 0.4, r0=-0.2)
		]),
		Bone("spine1", 0.4, r0=-pi, sim=True, c=[
			Bone("spine2", 0.3, r0=0, sim=True, c=[
				Bone("head", 0.1, r0=0),
				Bone("upper_arm_l", 0.4, r0=pi+0.5, c=[
					Bone("lower_arm_l", 0.4, r0=-0.3)
				]),
				Bone("upper_arm_r", 0.4, r0=pi-0.5, c=[
					Bone("lower_arm_r", 0.4, r0=+0.3)
				])
			])
		])
	])

test_bone = \
	Bone("root", 0, r0=0, sim=False, c=[
		Bone("b1", 0.5, r0=0.5, c=[
			Bone("b2", 0.5, r0=+0.5)
		])
	])

root = pelvis

world = b2World(gravity=(0, -9.8))

floor_shape = b2PolygonShape()
floor_shape.SetAsBox(2, 0.1)

floor_fixt = b2FixtureDef()
floor_fixt.shape = floor_shape

world.CreateStaticBody(fixtures=floor_fixt, position=(0, -1.2))

init_bone(root, 0, Vec2(0, 0), world)

width = 900
height = 600
screen = pygame.display.set_mode((width, height))

t = 0
fps = 60
clock = pygame.time.Clock()
while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
	
	screen.fill((0, 0, 0))
	
	world.Step(1 / fps, 6, 3)
	update_bone(root)
	draw_bone(root, screen)
	
	pygame.display.flip()
	pygame.display.update()
	
	t += clock.tick(fps) / 1000
