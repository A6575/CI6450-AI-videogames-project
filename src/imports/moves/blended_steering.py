from imports.moves.kinematic import SteeringOutput
from imports.moves.evade import Evade
from imports.moves.pursue import Pursue
from imports.moves.look_where_youre_going import LookWhereYoureGoing
from pygame.math import Vector2

class BlendedSteeringLWYG:
	def __init__(self, character, movement_behavior, explicit_target):
		self.character = character					# El personaje que usa blended steering (NPC)	
		self.movement_behavior = movement_behavior 	# Diccionario con {"comportamiento": parametros}
			# Ejemplo: {"Pursue": {"max_prediction": 1.0, "pursue_target": target}}
		self.explicit_target = explicit_target		# El objetivo explícito para la orientación para Pursue o Evade (Player)

	def get_steering(self):
		# Inicializar los resultados de los comportamientos
		result_steering = SteeringOutput(Vector2(0, 0), 0)
		movement_steering = SteeringOutput(Vector2(0, 0), 0)

		for behavior, params in self.movement_behavior.items():
			# Dependiendo del comportamiento, crear la instancia correspondiente y obtener el steering
			if behavior == "Pursue":
				pursue = Pursue(character=self.character, explicit_target=self.explicit_target, **params)
				movement_steering = pursue.get_steering()
			elif behavior == "Evade":
				evade = Evade(character=self.character, explicit_target=self.explicit_target, **params)
				movement_steering = evade.get_steering()

		# Obtener el steering de LookWhereYoureGoing
		lwyg_steering = LookWhereYoureGoing(character=self.character, explicit_target=self.explicit_target).get_steering()
		# Combinar los resultados
		result_steering.linear += movement_steering.linear
		result_steering.angular += lwyg_steering.angular
		return result_steering