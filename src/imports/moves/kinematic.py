# Algoritmos de movimiento
import math
from pygame import Vector2

class KinematicSteeringOutput:
	def __init__(self, velocity, rotation):
		self.velocity = velocity  # Vector2
		self.rotation = rotation  # float
class SteeringOutput:
	def __init__(self, linear, angular):
		self.linear = linear	# Vector2
		self.angular = angular	# float

class Kinematic:
	def __init__(self, position, velocity, orientation, rotation):
		self.position = position 			# Vector2
		self.velocity = velocity 			# Vector2
		self.orientation = orientation 		# float
		self.rotation = rotation 			# float

	def update(self, steering, time, character_rect, obstacles, max_speed=float('inf'), uses_rotation=False):
		# Movimiento en el eje X
		self.position.x += self.velocity.x * time
		character_rect.centerx = int(self.position.x)
		# Se comprueba si hay colisión después de mover en X.
		if self._check_collision(character_rect, obstacles):
			# Si hay colisión, se revierte el movimiento en X.
			self.position.x -= self.velocity.x * time
			# Se anula la velocidad en este eje para detener el movimiento en esta dirección.
			self.velocity.x = 0
			character_rect.centerx = int(self.position.x)

		# Movimiento en el eje Y
		self.position.y += self.velocity.y * time
		character_rect.centery = int(self.position.y)
		# Se comprueba si hay colisión después de mover en Y.
		if self._check_collision(character_rect, obstacles):
			# Si hay colisión, se revierte el movimiento en Y.
			self.position.y -= self.velocity.y * time
			# Se anula la velocidad en este eje.
			self.velocity.y = 0
			character_rect.centery = int(self.position.y)

		if uses_rotation:
			self.orientation += self.rotation*time
		else:
			self.orientation = self.new_orientation()
		self.velocity += steering.linear * time
		self.rotation += steering.angular * time

		if self.velocity.length() > max_speed:
			self.velocity = self.velocity.normalize() * max_speed

	def _check_collision(self, character_rect, obstacles):
		if not obstacles:
			return False
			
		# Itera sobre cada obstáculo para comprobar la colisión.
		for shape_type, shape_data in obstacles:
			if shape_type == 'rect':
				# Si el obstáculo es un rectángulo, usa colliderect.
				if character_rect.colliderect(shape_data):
					return True
			elif shape_type == 'poly':
				# Si es un polígono, comprueba si alguna de sus líneas se cruza con el rect.
				if character_rect.clipline(shape_data[0], shape_data[1]) or \
					character_rect.clipline(shape_data[1], shape_data[2]) or \
					character_rect.clipline(shape_data[2], shape_data[0]):
					return True
		return False
	
	def new_orientation(self, velocity=None, orientation=None):
		if velocity is None:
			velocity = self.velocity
		if orientation is None:
			orientation = self.orientation

		if velocity.length() > 0:
			return math.degrees(math.atan2(-velocity.x, -velocity.y))
		return orientation
	
	def orientation_to_vector(self):
		radians = math.radians(self.orientation)
		return Vector2(-math.sin(radians), -math.cos(radians))