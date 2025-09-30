# Algoritmos de movimiento

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
		self.orientation += self.rotation * time
		self.velocity += steering.linear * time
		self.rotation += steering.angular * time