from imports.moves.kinematic import SteeringOutput
from imports.moves.evade import Evade
from imports.moves.pursue import Pursue
from imports.moves.look_where_youre_going import LookWhereYoureGoing
from pygame.math import Vector2

class BlendedSteeringLWYG:
	def __init__(self, character, movement_behavior, explicit_target):
		self.character = character
		self.movement_behavior = movement_behavior # Diccionario con {comportamiento: parametros}
			# Ejemplo: {"DynamicWander": {max_acceleration: 10, wander_target: NPC(...), ...}, "Face": {max_rotation: 50, ...}}
		self.explicit_target = explicit_target

	def get_steering(self):
		result_steering = SteeringOutput(Vector2(0, 0), 0)
		movement_steering = SteeringOutput(Vector2(0, 0), 0)
		for behavior, params in self.movement_behavior.items():
			if behavior == "Pursue":
				pursue = Pursue(character=self.character, explicit_target=self.explicit_target, **params)
				movement_steering = pursue.get_steering()
			elif behavior == "Evade":
				evade = Evade(character=self.character, explicit_target=self.explicit_target, **params)
				movement_steering = evade.get_steering()

		lwyg_steering = LookWhereYoureGoing(character=self.character, explicit_target=self.explicit_target).get_steering()
		result_steering.linear += movement_steering.linear
		result_steering.angular += lwyg_steering.angular
		return result_steering