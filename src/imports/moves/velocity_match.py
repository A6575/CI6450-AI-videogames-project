from imports.moves.kinematic import SteeringOutput
from pygame.math import Vector2

class VelocityMatch:
	def __init__(self, character, target, max_acceleration, time_to_target):
		self.character = character
		self.target = target
		self.max_acceleration = max_acceleration
		self.time_to_target = time_to_target
	
	def get_steering(self):
		result = SteeringOutput(Vector2(0, 0), 0)
		
		# Calculate the linear acceleration needed to match the target's velocity
		result.linear = (self.target.kinematic.velocity - self.character.kinematic.velocity) / self.time_to_target
		
		# Limit the linear acceleration to max acceleration
		if result.linear.length() > self.max_acceleration:
			result.linear = result.linear.normalize() * self.max_acceleration
		
		return result