from imports.moves.kinematic import SteeringOutput
from pygame.math import Vector2
from math import pi

class Align:
	def __init__(self, character, target, max_rotation, max_angular_acceleration, target_radius, slow_radius, time_to_target):
		self.character = character
		self.target = target
		self.max_rotation = max_rotation
		self.max_angular_acceleration = max_angular_acceleration
		self.target_radius = target_radius
		self.slow_radius = slow_radius 
		self.time_to_target = time_to_target
	
	def get_steering(self):
		steering = SteeringOutput(Vector2(0, 0), 0)
		
		# Calculate the direction to the target
		direction = self.target.kinematic.orientation - self.character.kinematic.orientation
		direction = (direction + 180) % (2 * 180) - 180  # Normalize to [-180, 180]
		distance = abs(direction)

		# Check if we are within the target radius
		if distance < self.target_radius:
			return steering  # No steering needed
		
		# Determine the target rotation speed
		if distance > self.slow_radius:
			target_rotation = self.max_rotation
		else:
			target_rotation = self.max_rotation * distance / self.slow_radius
		
		# Adjust the target rotation direction
		target_rotation *= direction / distance
		
		# Calculate the angular acceleration needed to reach the target rotation
		steering.angular = (target_rotation - self.character.kinematic.rotation) / self.time_to_target
		
		# Limit the angular acceleration to max angular acceleration
		if abs(steering.angular) > self.max_angular_acceleration:
			steering.angular = (steering.angular / abs(steering.angular)) * self.max_angular_acceleration
	
		return steering