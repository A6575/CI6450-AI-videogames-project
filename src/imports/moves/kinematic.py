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

	def new_orientation(self):
		if self.velocity.length() > 0:
			return math.degrees(math.atan2(-self.velocity.x, -self.velocity.y))
		return self.orientation