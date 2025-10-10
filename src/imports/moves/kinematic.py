# Algoritmos de movimiento
import math
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

	def update(self, steering, time):
		self.position += self.velocity * time
		self.orientation = self.new_orientation()
		self.velocity += steering.linear * time
		self.rotation += steering.angular * time

	def new_orientation(self, velocity=None, orientation=None):
		if velocity is None:
			velocity = self.velocity
		if orientation is None:
			orientation = self.orientation

		if velocity.length() > 0:
			return math.degrees(math.atan2(-velocity.x, -velocity.y))
		return orientation