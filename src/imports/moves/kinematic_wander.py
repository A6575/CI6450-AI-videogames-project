import math
import random
from pygame.math import Vector2
from imports.moves.kinematic import KinematicSteeringOutput

class KinematicWander:
	def __init__(self, character, max_speed, max_rotation):
		self.character = character
		self.max_speed = max_speed
		self.max_rotation = max_rotation

	def _random_binomial(self):
		return random.random() - random.random()
	
	def get_steering(self) -> KinematicSteeringOutput:
		result = KinematicSteeringOutput(Vector2(0, 0), 0)

		result.velocity = self.character.kinematic.orientation_to_vector() * self.max_speed

		result.rotation = self._random_binomial() * self.max_rotation # type: ignore

		return result