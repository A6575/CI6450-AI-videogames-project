from pygame.math import Vector2
from imports.moves.kinematic import SteeringOutput

class DynamicFlee:
	def __init__(self, character, target, max_acceleration):
		self.character = character
		self.target = target
		self.max_acceleration = max_acceleration

	def get_steering(self):
		result = SteeringOutput(Vector2(0, 0), 0)
		result.linear = self.character.kinematic.position - self.target.kinematic.position
		
		if result.linear.length() == 0:
			return result  # No steering needed if on the same position
		
		result.linear = result.linear.normalize() * self.max_acceleration
		result.angular = 0
		return result