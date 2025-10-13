import math
import random
from pygame.math import Vector2
from imports.moves.kinematic import KinematicSteeringOutput

class KinematicWander:
	def __init__(self, character, max_speed, max_rotation):
		self.character = character			# El personaje que deambulará (NPC)
		self.max_speed = max_speed			# La velocidad máxima del personaje
		self.max_rotation = max_rotation	# La rotación máxima del personaje

	def _random_binomial(self):
		# Genera un valor aleatorio entre -1 y 1
		return random.random() - random.random()
	
	def get_steering(self):
		result = KinematicSteeringOutput(Vector2(0, 0), 0)

		# La velocidad es en la dirección de la orientación actual
		result.velocity = self.character.kinematic.orientation_to_vector() * self.max_speed

		# La rotación es un valor aleatorio entre -max_rotation y max_rotation
		result.rotation = self._random_binomial() * self.max_rotation # type: ignore

		return result