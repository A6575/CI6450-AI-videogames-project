from imports.moves.kinematic import SteeringOutput
from imports.moves.dynamic_seek import DynamicSeek
from pygame.math import Vector2

class ObstacleAvoidance:
	def __init__(self, character, obstacles, explicit_target, avoid_distance, lookahead, max_acceleration):
		self.character = character
		self.obstacles = obstacles
		self.explicit_target = explicit_target
		self.avoid_distance = avoid_distance
		self.lookahead = lookahead
		self.max_acceleration = max_acceleration

	def _ray_intersects_rect(self, ray_start, ray_end, rect):
		return rect.clipline(ray_start, ray_end)
	def get_steering(self):
		if self.character.kinematic.velocity.length_squared() == 0:
			return SteeringOutput(Vector2(0, 0), 0)  # No movement, no avoidance needed

		ray_vector = self.character.kinematic.velocity.normalize() * self.lookahead
		ray_start = self.character.kinematic.position
		ray_end = ray_start + ray_vector

		closest_collision = None
		closest_distance = float('inf')

		for obstacle in self.obstacles:
			collision = self._ray_intersects_rect(ray_start, ray_end, obstacle)
			if collision:
				collision_point = Vector2(collision[0])
				distance = (collision_point - ray_start).length()
				if distance < closest_distance:
					closest_distance = distance

					center_collision = collision_point - Vector2(obstacle.width/2, obstacle.height/2)
					
					dx = abs(center_collision.x) / (obstacle.width / 2)
					dy = abs(center_collision.y) / (obstacle.height / 2)

					normal = Vector2(0, 0)
					if dx > dy:
						normal.x = 1 if center_collision.x > 0 else -1
					else:
						normal.y = 1 if center_collision.y > 0 else -1
					
					closest_collision = {"point": collision_point, "normal": normal}

		if not closest_collision:
			return SteeringOutput(Vector2(0, 0), 0)  # No avoidance needed

		self.explicit_target.kinematic.position = closest_collision["point"] + closest_collision["normal"] * int(self.avoid_distance)
		
		seek = DynamicSeek(
			self.character,
			self.explicit_target,
			self.max_acceleration
		)

		return seek.get_steering()