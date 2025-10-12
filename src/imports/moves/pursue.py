from imports.moves.dynamic_arrive import DynamicArrive

class Pursue:
	def __init__(self, character, pursue_target, max_prediction, explicit_target, max_acceleration=100, max_speed=100):
		self.character = character
		self.pursue_target = pursue_target
		self.max_prediction = max_prediction
		self.explicit_target = explicit_target
		self.max_acceleration = max_acceleration
		self.max_speed = max_speed

	def get_steering(self):
		# Vector desde el perseguidor al objetivo
		direction = self.pursue_target.kinematic.position - self.character.kinematic.position
		distance = direction.length()

		# Velocidad relativa
		speed = self.character.kinematic.velocity.length()

		# Tiempo de predicción
		if speed <= distance / self.max_prediction:
			prediction = self.max_prediction
		else:
			prediction = distance / speed if speed != 0 else 0

		# Posición futura del objetivo
		self.explicit_target.kinematic.position = self.pursue_target.kinematic.position + self.pursue_target.kinematic.velocity * prediction

		# Usar DynamicArrive para llegar a la posición futura
		arrive = DynamicArrive(
			character=self.character,
			target=self.explicit_target,
			max_acceleration=self.max_acceleration,
			max_speed=self.max_speed,
			target_radius=3,
			slow_radius=50,
			time_to_target=0.1
		)
		return arrive.get_steering()