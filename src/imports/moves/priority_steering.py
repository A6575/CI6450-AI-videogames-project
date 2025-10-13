from imports.moves.kinematic import SteeringOutput
from imports.moves.obstacle_avoidance import ObstacleAvoidance
from imports.moves.blended_steering import BlendedSteeringLWYG
from pygame.math import Vector2

class PrioritySteering:
	def __init__(self, character, behaviors):
		self.character = character
		self.behaviors = behaviors  # Diccionario con ["comportamiento": parametros]
		self.algos = []
		if "ObstacleAvoidance" in behaviors:
			self.algos.append(ObstacleAvoidance(character=self.character, **self.behaviors["ObstacleAvoidance"]))
		if "BlendedSteeringLWYG" in behaviors:
			self.algos.append(BlendedSteeringLWYG(character=self.character, **self.behaviors["BlendedSteeringLWYG"]))

	def get_steering(self):
		for alg in self.algos:
			result = alg.get_steering()

			if result and (result.linear.length_squared() > 0 or result.angular != 0):
				return result
		
		return SteeringOutput(Vector2(0, 0), 0)  # No avoidance needed