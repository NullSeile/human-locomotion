from typing import Tuple, List, Dict
import sys
import pygame
from pygame import gfxdraw
from pygame.locals import QUIT
from Box2D import b2World, b2PolygonShape, b2CircleShape, b2FixtureDef, b2Body, b2_dynamicBody, b2_staticBody

from math import pi

from utils import to_screen_pos

Vec2 = Tuple[float, float]

class BodyPart:
	def __init__(self, vertices, pos: Vec2, angle: float, world: b2World, dynamic: bool = True):
		self.shape = b2PolygonShape()
		self.shape.vertices = vertices
		self.fixture = b2FixtureDef(
			shape=self.shape,
			density=1,
			friction=0.5,
			# categoryBits=0x0020,
			# maskBits=0x001
		)
		body_type = b2_dynamicBody if dynamic else b2_staticBody
		self.body: b2Body = world.CreateBody(
			type=body_type,
			fixtures=self.fixture,
			position=pos,
			angle=angle,
			# angularDamping=10,
			# linearDamping=1
		)
		
	def draw(self, screen: pygame.Surface, center: Vec2, radius: float):
		trans = self.body.transform
		
		path = [to_screen_pos(trans * v, center, radius, screen) for v in self.shape.vertices]
		gfxdraw.filled_polygon(screen, path, (255, 255, 255))
		gfxdraw.aapolygon(screen, path, (255, 255, 255))
		pygame.draw.polygon(screen, color=(120, 120, 120), points=path, width=1)

def CreateJoint(bodyA: BodyPart, bodyB: BodyPart, anchorA: Vec2, anchorB: Vec2, world: b2World):
	world.CreateRevoluteJoint(
		bodyA=bodyA.body,
		bodyB=bodyB.body,
		localAnchorA=anchorA,
		localAnchorB=anchorB,
		collideConnected=False
	)

if __name__ == "__main__":
	world = b2World(gravity=(0, -9.8))
	
	width = 900
	height = 600
	screen = pygame.display.set_mode((width, height))
	
	parts: Dict[str, BodyPart] = {
		'floor': BodyPart([(-5, 0.1), (5, 0.1), (5, -0.1), (-5, -0.1)], (0, -2), .5, world, dynamic=False),
		'b1': BodyPart([(-1, -0.2), (1, -0.2), (1, 0.5), (-1, 0.2)], (0, 0), 0, world),
		'b2': BodyPart([(-1, -0.2), (1, -0.2), (1, 0.6), (-1, 0.1)], (0, 0), 0.2, world)
	}
	
	CreateJoint(parts['b1'], parts['b2'], (1, 0), (-1, 0), world)
	
	
	fps = 60
	world.Step(1 / fps, 6, 3)
	clock = pygame.time.Clock()
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
		
		screen.fill((0, 0, 0))
		
		world.Step(1 / fps, 6, 3)
		
		for b in parts.values():
			b.draw(screen, (0, 0), 3)
		
		pygame.display.flip()
		pygame.display.update()
		
		clock.tick(fps) / 1000