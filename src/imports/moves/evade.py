from imports.moves.dynamic_flee import DynamicFlee

class Evade:
	def __init__(self, character, evade_target, max_prediction, explicit_target, max_acceleration=10):
		self.character = character
		self.evade_target = evade_target
		self.max_prediction = max_prediction
		self.explicit_target = explicit_target
		self.max_acceleration = max_acceleration
	
	def get_steering(self):
		# Vector desde el perseguidor al objetivo
		direction = self.evade_target.kinematic.position - self.character.kinematic.position
		distance = direction.length()

		# Velocidad relativa
		speed = self.character.kinematic.velocity.length()

		# Tiempo de predicción
		if speed <= distance / self.max_prediction:
			prediction = self.max_prediction
		else:
			prediction = distance / speed if speed != 0 else 0

		# Posición futura del objetivo
		self.explicit_target.kinematic.position = self.evade_target.kinematic.position + self.evade_target.kinematic.velocity * prediction

		# Usar DynamicFlee para alejarse de la posición futura
		flee = DynamicFlee(
			character=self.character,
			target=self.explicit_target,
			max_acceleration=self.max_acceleration
		)
		return flee.get_steering()