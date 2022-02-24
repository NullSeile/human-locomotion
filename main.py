import pygame
from pygame.locals import *
import sys
from typing import Callable, Tuple
from math import *

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

class Bone:
	def __init__(self, name: str, length: float, r0: float = 0, f: Callable[[float], float] = None, sim: bool = True, c: list = []):
		self.name = name
		self.length = length
		self.children = c
		self.function = f
		self.simulate = sim
		self.rotation = r0
		self.angular_vel = 0

# Maps a float x, which goes from x0 to x1, to go from y0 to y1
def map(x: float, x0: float, x1: float, y0: float, y1: float):
	return y0 + ((y1 - y0) / (x1 - x0)) * (x - x0)

def to_screen_pos(pos: Point, center: Point, radius: float, screen: pygame.Surface) -> Tuple[int, int]:
	width = screen.get_width()
	height = screen.get_height()
	
	aspect = width / height
	
	x = map(pos.x, center.x - radius*aspect, center.x + radius*aspect, 0, width)
	y = map(pos.y, center.y - radius, center.y + radius, 0, height)
	
	return x, y

def update_bone(bone: Bone, t: float):
	if bone.function is not None:
		bone.rotation = bone.function(t)
	
	for bone_child in bone.children:
		update_bone(bone_child, t)
		
def sim_bone(bone: Bone, rot: float, dt: float):
	global_rot = rot + bone.rotation
	
	if bone.simulate:
		bone.rotation += bone.angular_vel*dt
		
		weight = bone.length * 10*cos(global_rot)
		drag = bone.angular_vel * 1
		
		bone.angular_vel += (weight - drag) * dt
	
	for bone_child in bone.children:
		sim_bone(bone_child, global_rot, dt)

center = Point(0, 0)
radius = 1.5
def draw_bone(bone: Bone, pos: Point, parent_rotation: float, screen: pygame.Surface):
	rotation = parent_rotation + bone.rotation
	next_pos = Point(pos.x + bone.length * cos(rotation), pos.y + bone.length * sin(rotation))
	
	pygame.draw.line(screen, (255, 255, 255),
						  to_screen_pos(pos, center, radius, screen),
						  to_screen_pos(next_pos, center, radius, screen), 5)
	
	for bone_child in bone.children:
		draw_bone(bone_child, next_pos, rotation, screen)

pelvis = \
	Bone("pelvis", 0, r0=pi/2 + 0.2, sim=False, c=[
		Bone("femur_l", 0.5, r0=-0.4, c=[
			Bone("tibia_l", 0.4, r0=0.2)
		]),
		Bone("femur_r", 0.5, r0=0.5, c=[
			Bone("tibia_r", 0.4, r0=-0.2)
		]),
		Bone("spine1", 0.4, r0=-pi, sim=False, c=[
			Bone("spine2", 0.3, r0=0, c=[
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
			Bone("b2", 0.5, r0=0)
		])
	])

width = 900
height = 900
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
	
	# update_bone(pelvis, t)
	# draw_bone(pelvis, Point(0, 0), 0, screen)
	
	# update_bone(test_bone, t)
	sim_bone(pelvis, 0, 2/fps)
	draw_bone(pelvis, Point(0, 0), 0, screen)
	
	pygame.display.update()
	
	t += clock.tick(fps) / 1000
