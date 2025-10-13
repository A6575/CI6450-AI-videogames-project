from imports.moves.kinematic import SteeringOutput
from pygame.math import Vector2

class DynamicArrive:
	def __init__(self, character, target, max_acceleration, max_speed, target_radius, slow_radius, time_to_target=0.1):
		self.character = character						# El personaje que se va a mover (NPC)
		self.target = target							# El objetivo al que se va a mover (Player)
		self.max_acceleration = max_acceleration		# La aceleración máxima del personaje
		self.max_speed = max_speed						# La velocidad máxima del personaje
		self.target_radius = target_radius				# El radio objetivo para la llegada
		self.slow_radius = slow_radius					# El radio de desaceleración
		self.time_to_target = time_to_target			# El tiempo para alcanzar el objetivo

	def get_steering(self):
		result = SteeringOutput(Vector2(0, 0), 0)

		# Calcular la direccion del target
		direction = self.target.kinematic.position - self.character.kinematic.position
		distance = direction.length()

		# Comprobar si estamos dentro del radio objetivo
		if distance < self.target_radius:
			return result  # No se necesita dirección

		# Determinar la velocidad de destino
		if distance > self.slow_radius:
			target_speed = self.max_speed
		else:
			target_speed = self.max_speed * distance / self.slow_radius

		# Calcular la velocidad objetivo
		if distance > 0:
			target_velocity = direction.normalize() * target_speed
		else:
			target_velocity = Vector2(0, 0)

		# Calcular la aceleración necesaria para alcanzar la velocidad objetivo
		result.linear = (target_velocity - self.character.kinematic.velocity) / self.time_to_target

		# Comprobar si la aceleración es demasiado grande
		if result.linear.length() > self.max_acceleration:
			result.linear = result.linear.normalize() * self.max_acceleration

		result.angular = 0  # No hay aceleración angular para el comportamiento de llegada

		return result