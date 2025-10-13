from imports.moves.kinematic import SteeringOutput
from imports.moves.collision_avoidance import CollisionAvoidance
from imports.moves.dynamic_wander import DynamicWander
from pygame.math import Vector2

class PrioritySteering:
	def __init__(self, character, behaviors):
		self.character = character
		self.behaviors = behaviors  # Diccionario con ["comportamiento": parametros]
		self.algos = [CollisionAvoidance(character=self.character, **self.behaviors["CollisionAvoidance"]),
					  DynamicWander(character=self.character, **self.behaviors["DynamicWander"])]
			# Ejemplo: {"CollisionAvoidance": {obstacles: [...], radius: 5, max_acceleration: 100}, "Evade": {evade_target: NPC(...), max_prediction: 1.0}}

	def get_steering(self):
		for alg in self.algos:
			result = alg.get_steering()

			if result and (result.linear.length_squared() > 0 or result.angular != 0):
				return result
		
		return SteeringOutput(Vector2(0, 0), 0)  # No avoidance needed