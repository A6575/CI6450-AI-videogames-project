from pygame.math import Vector2
from imports.moves.kinematic import SteeringOutput
class DynamicFlee:
	def __init__(self, character, target, max_acceleration):
		self.character = character						# El personaje que se va a mover (NPC)
		self.target = target							# El objetivo al que se va a alejar (Player)
		self.max_acceleration = max_acceleration		# La aceleración máxima del personaje

	def get_steering(self):
		result = SteeringOutput(Vector2(0, 0), 0)
		
		# Calcular la direccion del target
		result.linear = self.character.kinematic.position - self.target.kinematic.position
		
		if result.linear.length() == 0:
			return result  # No se necesita dirección si están en la misma posición
		
		# Normalizar y escalar a la aceleración máxima
		result.linear = result.linear.normalize() * self.max_acceleration
		result.angular = 0 # No hay aceleración angular para el comportamiento de huida
		return result