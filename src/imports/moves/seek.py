from pygame.math import Vector2

class Seek:
	def __init__(self, character, target, max_speed):
		self.character = character
		self.target = target
		self.max_speed = max_speed

	def get_kinematic_steering(self) -> Vector2:
		# Calculate the direction to the target
		direction = self.target.kinematic.position - self.character.kinematic.position
		if direction.length() == 0:
			return Vector2(0, 0)

		# Normalize the direction and scale by max speed
		result_velocity = direction.normalize() * self.max_speed

		# Set the character's velocity to the desired velocity
		self.character.kinematic.velocity = result_velocity
		self.character.kinematic.orientation = self.character.kinematic.new_orientation()

		return result_velocity
	
	def get_dynamic_steering(self):
		pass