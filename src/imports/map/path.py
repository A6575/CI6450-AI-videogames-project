from pygame.math import Vector2
import math
class Path:
	def __init__(self, init_point, rectangular=True):
		self.init_point = init_point  # Punto inicial (Vector2) del camino
		self.points = [init_point]  # Lista de puntos (Vector2) que forman el camino
		self.rectangular = rectangular  # Indica si el camino es rectangular o no

	# Genera un camino rectangular alrededor del punto inicial
	def _generate_rectangular_path(self, width=300, height=200, num_points=100):
		x, y = self.init_point.x, self.init_point.y
		points = []
		# Calculate points per side (distribute evenly)
		sides = [width, height, width, height]
		total_length = sum(sides)
		segment_lengths = [int(num_points * (side / total_length)) for side in sides]
		# Adjust to ensure total points is num_points
		diff = num_points - sum(segment_lengths)
		for i in range(abs(diff)):
			segment_lengths[i % 4] += 1 if diff > 0 else -1

		# Top side (left to right)
		for i in range(segment_lengths[0]):
			px = x + (width * i) / segment_lengths[0]
			points.append(Vector2(px, y))
		# Right side (top to bottom)
		for i in range(segment_lengths[1]):
			py = y + (height * i) / segment_lengths[1]
			points.append(Vector2(x + width, py))
		# Bottom side (right to left)
		for i in range(segment_lengths[2]):
			px = x + width - (width * i) / segment_lengths[2]
			points.append(Vector2(px, y + height))
		# Left side (bottom to top)
		for i in range(segment_lengths[3]):
			py = y + height - (height * i) / segment_lengths[3]
			points.append(Vector2(x, py))
		# Close the path
		points.append(self.init_point)
		return points
	
	# Genera un camino circular alrededor del punto inicial
	def _generate_circular_path(self, radius=100, num_points=100):
		x, y = self.init_point.x, self.init_point.y
		points = []
		for i in range(num_points):
			angle = (2 * 3.14159 / num_points) * i
			point = Vector2(x + radius * math.cos(angle), y + radius * math.sin(angle))
			points.append(point)
		points.append(self.init_point)  # Cerrar el camino volviendo al punto inicial
		return points
	
	def get_path(self):
		if self.rectangular:
			return self._generate_rectangular_path()
		
		return self._generate_circular_path()
	
	# Determina el punto mas cercano en el camino a una posición dada
	def get_params(self, position):
		path = self.get_path()
		closest_point = min(path, key=lambda p: p.distance_to(position))
		# Encontrar el índice del punto más cercano
		try:
			closest_point_index = path.index(closest_point)
		except ValueError:
			# Si el punto no se encuentra, no podemos determinar la dirección
			return {
				"closest_point": closest_point,
				"distance": closest_point.distance_to(position),
				"path_direction": Vector2(0, 0) # Devuelve un vector nulo
			}

		# Determinar el siguiente punto en el camino para calcular la dirección
		# Usamos el operador módulo para que el camino sea cíclico
		next_point_index = (closest_point_index + 1) % len(path)
		next_point = path[next_point_index]

		# Calcular y normalizar el vector de dirección del camino
		path_direction = next_point - closest_point
		if path_direction.length() > 0:
			path_direction.normalize_ip()

		return {
			"closest_point": closest_point,
			"distance": closest_point.distance_to(position),
			"path_direction": path_direction
		}
	
	# Devuelve el punto con la distancia especificada desde una posición dada
	def get_point_at_distance(self, distance, position):
		path = self.get_path()
		if not path:
			return None
		
		# Encontrar el punto más cercano en el camino
		closest_point = min(path, key=lambda p: p.distance_to(position) >= distance)
		return closest_point
