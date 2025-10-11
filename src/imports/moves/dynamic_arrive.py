from imports.moves.kinematic import SteeringOutput
from pygame.math import Vector2

class DynamicArrive:
	def __init__(self, character, target, max_acceleration, max_speed, target_radius, slow_radius, time_to_target=0.1):
		self.character = character
		self.target = target
		self.max_acceleration = max_acceleration
		self.max_speed = max_speed
		self.target_radius = target_radius
		self.slow_radius = slow_radius
		self.time_to_target = time_to_target

	def get_steering(self) -> SteeringOutput:
		result = SteeringOutput(Vector2(0, 0), 0)

		# Calculate the direction to the target
		direction = self.target.kinematic.position - self.character.kinematic.position
		distance = direction.length()

		# Check if we are within the target radius
		if distance < self.target_radius:
			return result  # No steering needed

		# Determine the target speed
		if distance > self.slow_radius:
			target_speed = self.max_speed
		else:
			target_speed = self.max_speed * distance / self.slow_radius

		# Calculate the target velocity
		if distance > 0:
			target_velocity = direction.normalize() * target_speed
		else:
			target_velocity = Vector2(0, 0)

		# Calculate the linear acceleration
		result.linear = (target_velocity - self.character.kinematic.velocity) / self.time_to_target

		# Check if the acceleration is too great
		if result.linear.length() > self.max_acceleration:
			result.linear = result.linear.normalize() * self.max_acceleration

		result.angular = 0  # No angular acceleration for arrive behavior

		return result