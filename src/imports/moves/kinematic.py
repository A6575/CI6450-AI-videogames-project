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

	def update(self, steering, time, max_speed=float('inf'), uses_rotation=False):
		self.position += self.velocity * time
		if uses_rotation:
			self.orientation += self.rotation*time
		else:
			self.orientation = self.new_orientation()
		self.velocity += steering.linear * time
		self.rotation += steering.angular * time

		if self.velocity.length() > max_speed:
			self.velocity = self.velocity.normalize() * max_speed

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