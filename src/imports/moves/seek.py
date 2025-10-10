from pygame.math import Vector2
from imports.moves.kinematic import SteeringOutput

class Seek:
	def __init__(self, character, target, max_speed):
		self.character = character
		self.target = target
		self.max_speed = max_speed

	def get_kinematic_steering(self) -> SteeringOutput:
		# Calculate the direction to the target
		direction = self.target.kinematic.position - self.character.kinematic.position

		# Normalize the direction and scale by max speed
		result_velocity = direction.normalize() * self.max_speed

		self.character.kinematic.orientation = self.character.kinematic.new_orientation(
			result_velocity,
			self.character.kinematic.orientation
		)

		return SteeringOutput(result_velocity, 0)
	
	def get_dynamic_steering(self):
		pass