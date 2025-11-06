# Algoritmos de movimiento
import math
from pygame import Vector2, Rect

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
		last_safe_position = self.position.copy()
		# Movimiento en el eje X
		self.position.x += self.velocity.x * time
		character_rect.centerx = int(self.position.x)
		# Se comprueba si hay colisión después de mover en X.
		colliding_shape_type, colliding_shape_data = self._get_colliding_obstacle(character_rect, obstacles)
		if colliding_shape_type:
			# Si hay colisión, se resuelve.
			if colliding_shape_type == 'rect' and isinstance(colliding_shape_data, Rect):
				# Resolución para rectángulos válidos.
				if self.velocity.x > 0: # Moviéndose a la derecha
					character_rect.right = colliding_shape_data.left
				elif self.velocity.x < 0: # Moviéndose a la izquierda
					character_rect.left = colliding_shape_data.right
				self.position.x = character_rect.centerx
				self.velocity.x = 0
			else:
				# Resolución genérica (polígonos o datos inesperados): se revierte el movimiento en este eje.
				self.position.x -= self.velocity.x * time
				self.velocity.x = 0
				character_rect.centerx = int(self.position.x)

		# Movimiento en el eje Y
		self.position.y += self.velocity.y * time
		character_rect.centery = int(self.position.y)
		# Se comprueba si hay colisión después de mover en Y.
		colliding_shape_type, colliding_shape_data = self._get_colliding_obstacle(character_rect, obstacles)
		if colliding_shape_type:
			# Si hay colisión, se resuelve.
			if colliding_shape_type == 'rect' and isinstance(colliding_shape_data, Rect):
				# Resolución para rectángulos válidos.
				if self.velocity.y > 0: # Moviéndose hacia abajo
					character_rect.bottom = colliding_shape_data.top
				elif self.velocity.y < 0: # Moviéndose hacia arriba
					character_rect.top = colliding_shape_data.bottom
				self.position.y = character_rect.centery
				self.velocity.y = 0
			else:
				# Resolución genérica (polígonos o datos inesperados): se revierte el movimiento en este eje.
				self.position.y -= self.velocity.y * time
				self.velocity.y = 0
				character_rect.centery = int(self.position.y)
		if self._get_colliding_obstacle(character_rect, obstacles)[0] is not None:
			self.position = last_safe_position
			self.velocity = Vector2(0, 0) # Detener completamente para evitar vibraciones.
			character_rect.center = self.position

		if uses_rotation:
			self.orientation += self.rotation*time
		else:
			self.orientation = self.new_orientation()
		self.velocity += steering.linear * time
		self.rotation += steering.angular * time

		if self.velocity.length() > max_speed:
			self.velocity = self.velocity.normalize() * max_speed

	def _get_colliding_obstacle(self, character_rect, obstacles):
		if not obstacles:
			return None, None
		
		for shape_type, shape_data in obstacles:
			if shape_type == 'rect':
				if character_rect.colliderect(shape_data):
					return shape_type, shape_data
			elif shape_type == 'poly':
				# La colisión con polígonos es más compleja para el ajuste de posición,
				# por ahora se usa clipline solo para detección simple.
				if character_rect.clipline(shape_data[0], shape_data[1]) or \
					character_rect.clipline(shape_data[1], shape_data[2]) or \
					character_rect.clipline(shape_data[2], shape_data[0]):
					
					return shape_type, shape_data
		return None, None

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