from imports.moves.kinematic import SteeringOutput
from imports.moves.dynamic_seek import DynamicSeek
from pygame.math import Vector2

class ObstacleAvoidance:
	def __init__(self, character, obstacles, explicit_target, avoid_distance, lookahead, max_acceleration):
		self.character = character					# El personaje que evita obstáculos (NPC)
		self.obstacles = obstacles					# Lista de obstáculos a evitar
		self.explicit_target = explicit_target		# El objetivo explícito para la orientación (Player)
		self.avoid_distance = avoid_distance		# La distancia a la que el personaje debe evitar los obstáculos
		self.lookahead = lookahead					# La distancia de anticipación para la detección de obstáculos
		self.max_acceleration = max_acceleration	# La aceleración máxima del personaje

	def _ray_intersects_rect(self, ray_start, ray_end, rect):
		# Devuelve el punto de intersección si el rayo intersecta el rectángulo, de lo contrario None
		return rect.clipline(ray_start, ray_end)
	
	def get_steering(self):
		if self.character.kinematic.velocity.length_squared() == 0:
			return SteeringOutput(Vector2(0, 0), 0)  # No hay movimiento si la velocidad es cero
		
		# Calcular el rayo de anticipación
		ray_vector = self.character.kinematic.velocity.normalize() * self.lookahead
		ray_start = self.character.kinematic.position
		ray_end = ray_start + ray_vector

		# Inicializar la colisión más cercana
		closest_collision = None
		closest_distance = float('inf')

		# Iterar sobre los obstáculos para encontrar la colisión más cercana (getCollision)
		for obstacle in self.obstacles:
			collision = self._ray_intersects_rect(ray_start, ray_end, obstacle)
			if collision:
				# Hay una colisión, verificar si es la más cercana
				collision_point = Vector2(collision[0])
				distance = (collision_point - ray_start).length()
				if distance < closest_distance:
					closest_distance = distance
					
					# Calcular la normal del obstáculo en el punto de colisión
					center_collision = collision_point - Vector2(obstacle.width/2, obstacle.height/2)
					
					dx = abs(center_collision.x) / (obstacle.width / 2)
					dy = abs(center_collision.y) / (obstacle.height / 2)

					normal = Vector2(0, 0)
					if dx > dy:
						# La colisión está en los lados izquierdo o derecho
						normal.x = 1 if center_collision.x > 0 else -1
					else:
						# La colisión está en los lados superior o inferior
						normal.y = 1 if center_collision.y > 0 else -1
					
					closest_collision = {"point": collision_point, "normal": normal} # Guardar el punto y la normal de la colisión

		# Si no hay colisión, no hacer nada
		if not closest_collision:
			return SteeringOutput(Vector2(0, 0), 0)  # No se necesita evitar

		# Mover el objetivo explícito a una posición alejada del obstáculo
		self.explicit_target.kinematic.position = closest_collision["point"] + closest_collision["normal"] * int(self.avoid_distance)
		
		# Usar el comportamiento de DynamicSeek para moverse hacia el nuevo objetivo
		seek = DynamicSeek(
			self.character,
			self.explicit_target,
			self.max_acceleration
		)

		return seek.get_steering()