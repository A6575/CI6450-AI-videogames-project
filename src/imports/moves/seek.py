from pygame.math import Vector2

class KinematicSteeringOutput:
	def __init__(self, velocity, rotation):
		self.velocity = velocity  # Vector2
		self.rotation = rotation  # float
class KinematicSeek:
	def __init__(self, character, target, max_speed):
		self.character = character
		self.target = target
		self.max_speed = max_speed

	def get_steering(self) -> KinematicSteeringOutput:
		result = KinematicSteeringOutput(Vector2(0, 0), 0)
		# Calculate the direction to the target
		direction = self.target.kinematic.position - self.character.kinematic.position

		# Normalize the direction and scale by max speed
		result.velocity = direction.normalize() * self.max_speed

		self.character.kinematic.orientation = self.character.kinematic.new_orientation(
			result.velocity,
			self.character.kinematic.orientation
		)

		return result