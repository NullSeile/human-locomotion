from __future__ import annotations

class Vec2:
	def __init__(self, x: float = 0, y: float = 0):
		self.x = x
		self.y = y
	
	def __add__(self, other: Vec2) -> Vec2:
		return Vec2(self.x + other.x, self.y + other.y)
	
	def __iadd__(self, other: Vec2) -> Vec2:
		self.x += other.x
		self.y += other.y
		return self
	
	def __sub__(self, other: Vec2) -> Vec2:
		return Vec2(self.x - other.x, self.y - other.y)
	
	def __isub__(self, other: Vec2) -> Vec2:
		self.x -= other.x
		self.y -= other.y
		return self
	
	def __mul__(self, other: float) -> Vec2:
		return Vec2(self.x * other, self.y * other)
	
	def __truediv__(self, other: float) -> Vec2:
		return Vec2(self.x / other, self.y / other)
	
	def cross(self, other: Vec2) -> float:
		return self.x * other.x + self.y * other.y
	
	def length(self) -> float:
		return sqrt(self.x**2 + self.y**2)
	
	def normalize(self) -> Vec2:
		return self / self.length()
	
	def __str__(self) -> str:
		return f"({self.x}, {self.y})"