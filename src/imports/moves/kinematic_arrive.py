from pygame.math import Vector2
from imports.moves.kinematic import KinematicSteeringOutput

class KinematicArrive:
	def __init__(self, character, target, max_speed, target_radius=5.0, time_to_target=0.1):
		self.character = character				# El personaje que llega (NPC)
		self.target = target					# El objetivo al que se dirige (Player)
		self.max_speed = max_speed				# La velocidad máxima del personaje
		self.target_radius = target_radius		# El radio del objetivo
		self.time_to_target = time_to_target	# El tiempo para alcanzar el objetivo

	def get_steering(self):
		result = KinematicSteeringOutput(Vector2(0, 0), 0)
		
		# Calcular la dirección hacia el objetivo
		direction = self.target.kinematic.position - self.character.kinematic.position

		# Si estamos dentro del radio del objetivo, no hacer nada
		if direction.length() < self.target_radius:
			return result

		# Calcular la velocidad deseada
		result.velocity = direction / self.time_to_target
		
		# Limitar la velocidad a la velocidad máxima
		if result.velocity.length() > self.max_speed:
			result.velocity = result.velocity.normalize() * self.max_speed
		
		# Actualizar la orientación del personaje
		self.character.kinematic.orientation = self.character.kinematic.new_orientation(
			result.velocity,
			self.character.kinematic.orientation
		)

		return result