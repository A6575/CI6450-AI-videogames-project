from pygame.math import Vector2
from imports.moves.kinematic import SteeringOutput

class DynamicSeek:
	def __init__(self, character, target, max_acceleration):
		self.character = character
		self.target = target
		self.max_acceleration = max_acceleration

	def get_steering(self):
		result = SteeringOutput(Vector2(0, 0), 0)
		result.linear = self.target.kinematic.position - self.character.kinematic.position
		result.linear = result.linear.normalize() * self.max_acceleration
		result.angular = 0
		return result