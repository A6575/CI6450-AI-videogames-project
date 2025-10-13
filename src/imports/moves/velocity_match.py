from imports.moves.kinematic import SteeringOutput
from pygame.math import Vector2

class VelocityMatch:
	def __init__(self, character, target, max_acceleration, time_to_target):
		self.character = character					# El personaje que ajusta su velocidad (NPC)
		self.target = target						# El objetivo al que se quiere igualar la velocidad (Player)
		self.max_acceleration = max_acceleration	# La aceleración máxima permitida
		self.time_to_target = time_to_target		# El tiempo para alcanzar la velocidad objetivo

	def get_steering(self):
		result = SteeringOutput(Vector2(0, 0), 0)

		# Calcular la aceleración lineal necesaria para igualar la velocidad del objetivo
		result.linear = (self.target.kinematic.velocity - self.character.kinematic.velocity) / self.time_to_target

		# Limitar la aceleración lineal a la aceleración máxima
		if result.linear.length() > self.max_acceleration:
			result.linear = result.linear.normalize() * self.max_acceleration
		
		return result