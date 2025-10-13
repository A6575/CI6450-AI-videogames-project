from pygame.math import Vector2
from imports.moves.kinematic import SteeringOutput

class DynamicSeek:
	def __init__(self, character, target, max_acceleration):
		self.character = character					# El personaje que se va a mover (NPC)
		self.target = target						# El objetivo al que se va a mover (Player)
		self.max_acceleration = max_acceleration	# La aceleración máxima del personaje

	def get_steering(self):
		result = SteeringOutput(Vector2(0, 0), 0)
		# Calcular la direccion del target
		result.linear = self.target.kinematic.position - self.character.kinematic.position
		if result.linear.length() == 0:
			return result  # No se necesita dirección si ya estamos en la posición del objetivo
		# Normalizar y escalar a la aceleración máxima
		result.linear = result.linear.normalize() * self.max_acceleration
		result.angular = 0  # No hay aceleración angular para el comportamiento de búsqueda
		return result