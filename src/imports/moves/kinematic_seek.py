from pygame.math import Vector2
from imports.moves.kinematic import KinematicSteeringOutput

class KinematicSeek:
	def __init__(self, character, target, max_speed):
		self.character = character	# El personaje que busca (NPC)
		self.target = target		# El objetivo que busca (Player)
		self.max_speed = max_speed	# La velocidad máxima del personaje

	def get_steering(self):
		result = KinematicSteeringOutput(Vector2(0, 0), 0)
		# Calcular la dirección hacia el objetivo
		direction = self.target.kinematic.position - self.character.kinematic.position

		if direction.length() == 0:
			return result  # No se necesita steering si están en la misma posición

		# Normalizar la dirección y escalar por la velocidad máxima
		result.velocity = direction.normalize() * self.max_speed
		
		# Actualizar la orientación del personaje
		self.character.kinematic.orientation = self.character.kinematic.new_orientation(
			result.velocity,
			self.character.kinematic.orientation
		)

		return result