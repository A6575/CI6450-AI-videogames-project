import random
from imports.moves.face import Face

class DynamicWander:
	def __init__(self, character, max_acceleration, wander_target, explicit_target, wander_offset=8.0, wander_radius=10.0, wander_rate=0.9):
		self.character = character
		self.max_acceleration = max_acceleration
		self.wander_target = wander_target
		self.explicit_target = explicit_target
		self.wander_offset = wander_offset
		self.wander_radius = wander_radius
		self.wander_rate = wander_rate
		self.wander_orientation = 0.0

	def _random_binomial(self):
		return random.random() - random.random()
	
	def get_steering(self):
		self.wander_orientation += self._random_binomial() * self.wander_rate # type: ignore

		self.wander_target.kinematic.orientation = self.wander_orientation + self.character.kinematic.orientation
		self.wander_target.kinematic.position = self.character.kinematic.position + self.wander_offset * self.character.kinematic.orientation_to_vector()
		self.wander_target.kinematic.position += self.wander_radius * self.wander_target.kinematic.orientation_to_vector()
		
		face = Face(
			character=self.character,
			face_target=self.wander_target,
			explicit_target=self.explicit_target
		)

		result = face.get_steering()
		result.linear = self.max_acceleration * self.character.kinematic.orientation_to_vector()
		return result