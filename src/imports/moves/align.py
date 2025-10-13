from imports.moves.kinematic import SteeringOutput
from pygame.math import Vector2

class Align:
	def __init__(self, character, target, max_rotation, max_angular_acceleration, target_radius, slow_radius, time_to_target):
		self.character = character 									# El personaje que se va a mover (NPC)
		self.target = target										# El objetivo al que se va a alinear (Player)
		self.max_rotation = max_rotation							# La rotación máxima del personaje
		self.max_angular_acceleration = max_angular_acceleration	# La aceleración angular máxima del personaje
		self.target_radius = target_radius							# El radio objetivo para la alineación
		self.slow_radius = slow_radius								# El radio de desaceleración
		self.time_to_target = time_to_target						# El tiempo para alcanzar el objetivo

	def get_steering(self):
		steering = SteeringOutput(Vector2(0, 0), 0)
		
		# Calcular la direccion del target
		direction = self.target.kinematic.orientation - self.character.kinematic.orientation
		direction = (direction + 180) % (2 * 180) - 180  # Normalizar a [-180, 180] (grados)
		distance = abs(direction)

		# Comprobar si estamos dentro del radio objetivo
		if distance < self.target_radius:
			return steering  # No se necesita dirección

		# Determinar la velocidad de rotación objetivo
		if distance > self.slow_radius:
			target_rotation = self.max_rotation
		else:
			target_rotation = self.max_rotation * distance / self.slow_radius
		
		# Ajustar la velocidad de rotación según la dirección
		target_rotation *= direction / distance

		# Calcular la aceleración angular necesaria para alcanzar la rotación objetivo
		steering.angular = (target_rotation - self.character.kinematic.rotation) / self.time_to_target

		# Limitar la aceleración angular a la máxima aceleración angular
		if abs(steering.angular) > self.max_angular_acceleration:
			steering.angular = (steering.angular / abs(steering.angular)) * self.max_angular_acceleration
	
		return steering