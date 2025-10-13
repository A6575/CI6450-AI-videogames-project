from imports.moves.kinematic import SteeringOutput
from pygame.math import Vector2

class CollisionAvoidance:
	def __init__(self, character, all_characters, radius, max_acceleration=100):
		self.character = character
		self.obstacles = all_characters
		self.radius = radius
		self.max_acceleration = max_acceleration

	def get_steering(self):
		shortest_time = float('inf')
		first_obstacle = None
		first_min_separation = float('inf')
		first_min_distance = float('inf')
		first_relative_position = Vector2(0, 0)
		first_relative_velocity = Vector2(0, 0)

		for obstacle in self.obstacles:
			if obstacle == self.character:
				continue

			relative_position = obstacle.kinematic.position - self.character.kinematic.position
			relative_velocity = obstacle.kinematic.velocity - self.character.kinematic.velocity
			relative_speed = relative_velocity.length()

			if relative_speed == 0:
				continue  # No hay movimiento relativo
			
			# Calculate time to closest approach
			time_to_closest_approach = relative_position.dot(relative_velocity) / relative_speed**2
			
			distance = relative_position.length()
			min_separation = distance - relative_speed * time_to_closest_approach
			if min_separation > 2 * self.radius:
				continue  # No hay riesgo de colisión
			if time_to_closest_approach > 0 and time_to_closest_approach < shortest_time:
				shortest_time = time_to_closest_approach
				first_obstacle = obstacle
				first_min_separation = min_separation
				first_min_distance = distance
				first_relative_position = relative_position
				first_relative_velocity = relative_velocity
			
		if not first_obstacle:
			return SteeringOutput(Vector2(0, 0), 0)  # No avoidance needed

		if first_min_separation <= 0 or first_min_distance < 2 * self.radius:
			relative_position = first_obstacle.kinematic.position - self.character.kinematic.position
		else:
			relative_position = first_relative_position + first_relative_velocity * shortest_time

		return SteeringOutput(relative_position.normalize() * self.max_acceleration, 0)
