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
	def __init__(self, name: str, length: float, function: Callable[[float], float], children: list):
		self.name = name
		self.length = length
		self.children = children
		self.function = function
		self.rotation = 0

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
	bone.rotation = bone.function(t)
	
	for bone_child in bone.children:
		update_bone(bone_child, t)

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
	Bone("pelvis", 0, lambda t: 0, [
		Bone("femur_l", 0.5, lambda t: -0.4, [
			Bone("tibia_l", 0.4, lambda t: 0.2 + 0.5*t, [])
		]),
		Bone("femur_r", 0.5, lambda t: 0.5 + 0.3*cos(3*t), [
			Bone("tibia_r", 0.4, lambda t: -0.2 - 0.1*cos(3*t), [])
		]),
		Bone("spine", 0.7, lambda t: -pi, [
			Bone("head", 0.1, lambda t: 0.2*cos(8*t), []),
			Bone("upper_arm_l", 0.4, lambda t: pi + 0.5 + 0.1*cos(5*t), [
				Bone("lower_arm_l", 0.4, lambda t: -0.3 + 0.2*cos(5*t), [])
			]),
			Bone("upper_arm_r", 0.4, lambda t: pi - 0.5 + 0.1*cos(5*t), [
				Bone("lower_arm_r", 0.4, lambda t: 0.4 + 0.4*cos(5*t), [])
			])
		])
	])

width = 900
height = 900
screen = pygame.display.set_mode((width, height))

t = 0
clock = pygame.time.Clock()
while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
	
	screen.fill((0, 0, 0))
	
	update_bone(pelvis, t)
	draw_bone(pelvis, Point(0, 0), pi/2, screen)
	
	pygame.display.update()
	
	t += clock.tick(60) / 1000
