from math import *
import pygame
from pygame.locals import *
import sys
from typing import Callable, Tuple

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

class Bone:
	def __init__(self, name: str, length: float, func: Callable[[float], float], children: list = []):
		self.name = name
		self.l = length
		self.c = children
		self.f = func
		self.r = 0

def map(x: float, x0: float, x1: float, y0: float, y1: float):
	return y0 + ((y1 - y0) / (x1 - x0)) * (x - x0)

def to_screen_pos(pos: Point, center: Point, radius: float, screen: pygame.Surface) -> Tuple[int, int]:
	width = screen.get_width()
	height = screen.get_height()
	
	aspect = width / height
	
	x = map(pos.x, center.x - radius*aspect, center.x + radius*aspect, 0, width)
	y = map(pos.y, center.y - radius, center.y + radius, 0, height)
	
	return x, y

def update_bone(b: Bone, t: float):
	b.r = b.f(t)
	
	for c in b.c:
		update_bone(c, t)

def draw_bone(b: Bone, pos: Point, rot: float, screen: pygame.Surface):
	rot += b.r
	next_pos = Point(pos.x + b.l * cos(rot), pos.y + b.l * sin(rot))
	
	pygame.draw.line(screen, (255, 255, 255),
						  to_screen_pos(pos, Point(0, 0), 1.5, screen),
						  to_screen_pos(next_pos, Point(0, 0), 1.5, screen), 5)
	
	for c in b.c:
		draw_bone(c, next_pos, rot, screen)

r = \
	Bone("root", 0, lambda t: 0, [
		Bone("femur_l", 0.5, lambda t: -0.4, [
			Bone("tibia_l", 0.4, lambda t: 0.2, [])
		]),
		Bone("femur_r", 0.5, lambda t: 0.5 + 0.3*cos(3*t), [
			Bone("tibia_r", 0.4, lambda t: -0.2 - 0.1*cos(3*t), [])
		]),
		Bone("spine", 0.7, lambda t: -pi, [
			Bone("head", 0.1, lambda t: 0.1*cos(8*t), []),
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
	
	update_bone(r, t)
	draw_bone(r, Point(0, 0), pi/2, screen)
	
	pygame.display.update()
	
	t += clock.tick(60) / 1000
	
