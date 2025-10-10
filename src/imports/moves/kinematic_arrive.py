from pygame.math import Vector2
from imports.moves.kinematic_seek import KinematicSteeringOutput

class KinematicArrive:
	def __init__(self, character, target, max_speed, target_radius=5.0, slow_radius=50.0, time_to_target=0.1):
		self.character = character
		self.target = target
		self.max_speed = max_speed
		self.target_radius = target_radius
		self.time_to_target = time_to_target

	def get_steering(self) -> KinematicSteeringOutput:
		result = KinematicSteeringOutput(Vector2(0, 0), 0)
		# Calculate the direction to the target
		direction = self.target.kinematic.position - self.character.kinematic.position

		# Check if we are within the target radius
		if direction.length() < self.target_radius:
			return result  # No steering needed

		result.velocity = direction / self.time_to_target

		if result.velocity.length() > self.max_speed:
			result.velocity = result.velocity.normalize() * self.max_speed

		self.character.kinematic.orientation = self.character.kinematic.new_orientation(
			result.velocity,
			self.character.kinematic.orientation
		)

		return result