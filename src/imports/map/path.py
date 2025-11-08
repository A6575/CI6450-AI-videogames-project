from pygame.math import Vector2
import math
class Path:
	def __init__(self, init_point, rectangular=True):
		self.init_point = init_point  # Punto inicial (Vector2) del camino a partir del cual se generará el camino
			# Si rectangular es True, se genera un camino rectangular alrededor del punto inicial
			# Si rectangular es False, se genera un camino circular alrededor del punto inicial
		self.points = [init_point]  	# Lista de puntos (Vector2) que forman el camino
		self.rectangular = rectangular  # Indica si el camino es rectangular o no

	# Genera un camino rectangular a partir del punto inicial
	def _generate_rectangular_path(self, width=500, height=300, num_points=200):
		x, y = self.init_point.x, self.init_point.y
		points = []
		# Calcular la cantidad de puntos por lado proporcional al tamaño del rectángulo
		sides = [width, height, width, height]
		total_length = sum(sides)
		segment_lengths = [int(num_points * (side / total_length)) for side in sides]
		# Ajustar para asegurar que el total de puntos sea num_points
		diff = num_points - sum(segment_lengths)
		for i in range(abs(diff)):
			segment_lengths[i % 4] += 1 if diff > 0 else -1

		# Lado superior (de izquierda a derecha)
		for i in range(segment_lengths[0]):
			px = x + (width * i) / segment_lengths[0]
			points.append(Vector2(px, y))
		# Lado derecho (de arriba hacia abajo)
		for i in range(segment_lengths[1]):
			py = y + (height * i) / segment_lengths[1]
			points.append(Vector2(x + width, py))
		# Lado inferior (de derecha a izquierda)
		for i in range(segment_lengths[2]):
			px = x + width - (width * i) / segment_lengths[2]
			points.append(Vector2(px, y + height))
		# Lado izquierdo (de abajo hacia arriba)
		for i in range(segment_lengths[3]):
			py = y + height - (height * i) / segment_lengths[3]
			points.append(Vector2(x, py))
		# Cerrar el camino
		points.append(self.init_point)
		return points
	
	# Genera un camino circular alrededor del punto inicial
	def _generate_circular_path(self, radius=200, num_points=200):
		x, y = self.init_point.x, self.init_point.y
		points = []
		for i in range(num_points):
			angle = (2 * math.pi / num_points) * i
			point = Vector2(x + radius * math.cos(angle), y + radius * math.sin(angle))
			points.append(point)
		# Cerrar el camino volviendo al primer punto de la circunferencia (no al punto central)
		if points:
			points.append(points[0])
		return points
	
	# Devuelve el camino completo como una lista de puntos (Vector2)
	def get_path(self):
		if self.rectangular:
			return self._generate_rectangular_path()
		
		return self._generate_circular_path()
	
	# Determina el punto mas cercano en el camino a una posición dada
	def get_params(self, position):
		path = self.get_path()
		# Encontrar el punto más cercano en el camino en funcion de la distancia entre puntos
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

class AStarPath(Path):
	def __init__(self, points):
		super().__init__(None, rectangular=False)
		self.points = points  # Lista de puntos (Vector2) que forman el camino
	
	def get_path(self):
		return self.points
	
	def get_params(self, position):
		path = self.get_path()
		if not path or len(path) < 2:
			return {
				"closest_point": Vector2(0, 0),
				"segment_index": 0,
				"path_direction": Vector2(0, 0)
			}

		# Encuentra el segmento de línea más cercano a la posición del personaje.
		min_dist_sq = float('inf')
		closest_segment_index = -1
		closest_projection = None

		for i in range(len(path) - 1):
			p1 = path[i]
			p2 = path[i+1]
			l2 = p1.distance_squared_to(p2)

			if l2 == 0:
				dist_sq = position.distance_squared_to(p1)
				projection = p1
			else:
				t = max(0, min(1, (position - p1).dot(p2 - p1) / l2))
				projection = p1 + t * (p2 - p1)
				dist_sq = position.distance_squared_to(projection)
			
			if dist_sq < min_dist_sq:
				min_dist_sq = dist_sq
				closest_segment_index = i
				closest_projection = projection

		# Calcula la dirección del camino en el segmento más cercano.
		p1 = path[closest_segment_index]
		p2 = path[closest_segment_index + 1]
		path_direction = (p2 - p1).normalize() if p1 != p2 else Vector2(0, 0)

		# El "punto más cercano" para FollowPath es la propia posición del personaje,
		# ya que el offset se calcula a partir de ahí a lo largo de la dirección del camino.
		return {
			"closest_point": closest_projection,
			"segment_index": closest_segment_index,
			"path_direction": path_direction
		}
	
	def get_param(self, position):
		params = self.get_params(position)
		segment_index = params['segment_index']
		closest_point_on_path = params['closest_point']

		dist_to_segment = 0.0
		for i in range(segment_index):
			dist_to_segment += self.points[i].distance_to(self.points[i+1])

		dist_on_segment = self.points[segment_index].distance_to(closest_point_on_path)
		param = float(segment_index)
		segment_length = self.points[segment_index].distance_to(self.points[segment_index+1])
		if segment_length > 0:
			proportion_in_segment = dist_on_segment / segment_length
			param += proportion_in_segment
		
		return param
	
	def get_position(self, param):
		if param < 0:
			param  = 0
		
		segment_index = int(param)

		t = param - segment_index

		if segment_index >= len(self.points) - 1:
			return self.points[-1]
		
		p0 = self.points[segment_index]
		p1 = self.points[segment_index + 1]

		return p0.lerp(p1, t)