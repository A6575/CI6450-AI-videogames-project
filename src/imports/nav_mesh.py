from shapely.geometry import Polygon, Point
import pygame
from collections import deque
import pickle
import os
from pathlib import Path
class NavMesh:
	def __init__(self, mapa_tmx):
		self.nav_polygons = {}
		self.nodes = {}
		self.edges = []
		self.graph = {}

		# Sistema de cache para cargar el nav mesh
		project_root = Path(__file__).resolve().parents[2]
		cache_path = project_root / "src" / "database" / "nav_mesh.cache"
		
		if os.path.exists(cache_path):
			print("Cargando navegación desde caché...")
			self.load_from_cache(cache_path)
		else:
			print("Generando NavMesh y creando cache...")
			self.load_nav_mesh(mapa_tmx)
			self.save_to_cache(cache_path)
	
	def save_to_cache(self, path):
		path.parent.mkdir(parents=True, exist_ok=True)
		cache_data = {
			'polygons': self.nav_polygons,
			'nodes': self.nodes,
			'edges': self.edges,
			'graph': self.graph
		}
		with open(path, 'wb') as f:
			pickle.dump(cache_data, f)
		print(f"NavMesh guardada en el cache: {path}")

	def load_from_cache(self, path):
		with open(path, 'rb') as f:
			cache_data = pickle.load(f)
		self.nav_polygons = cache_data['polygons']
		self.nodes = cache_data['nodes']
		self.edges = cache_data['edges']
		self.graph = cache_data['graph']
		print("NavMesh cargada exitosamente desde el cache")

	def load_nav_mesh(self, mapa_tmx):
		for layer in mapa_tmx.layers:
			if layer.name == "nav_mesh":
				for obj in layer:
					if obj.type != "nodes" or not hasattr(obj, 'points'):
						continue
					
					abs_points = [(point[0], point[1]) for point in obj.points]
					if not abs_points:
						continue

					polygon = Polygon(abs_points)
					self.nav_polygons[obj.id] = polygon

					centroid = polygon.centroid
					self.nodes[obj.id] = (centroid.x, centroid.y)

		if not self.nav_polygons:
			raise ValueError("Navigation mesh layer 'nav_mesh' not found in the TMX file.")

		polygon_ids = list(self.nav_polygons.keys())

		for i in range(len(polygon_ids)):
			for j in range(i + 1, len(polygon_ids)):
				poly1 = self.nav_polygons[polygon_ids[i]]
				poly2 = self.nav_polygons[polygon_ids[j]]

				# Primero, se comprueba si los polígonos se intersectan.
				if poly1.intersects(poly2):
					# Se calcula la geometría de la intersección.
					intersection = poly1.intersection(poly2)
					# Se considera una arista válida si la intersección tiene una longitud mayor que cero.
					# Esto funciona para LineString (unión perfecta) y para pequeños polígonos de superposición,
					# pero ignora las uniones de un solo punto (que tienen longitud cero).
					if intersection.length > 0:
						self.edges.append((polygon_ids[i], polygon_ids[j]))
		
		# Se construye el grafo de adyacencia una vez cargadas las aristas.
		self.graph = {node_id: [] for node_id in self.nodes}
		for id1, id2 in self.edges:
			self.graph[id1].append(id2)
			self.graph[id2].append(id1)

	def draw_nav_mesh(self, surface, camera_offset=(0, 0), active_nodes=None, graph_color=(0, 0, 255), poly_color=(150, 150, 150), active_poly_color=(0,255,0)):
		if active_nodes is None:
			active_nodes = []
		
		# Itera sobre cada polígono que Shapely ha generado.
		for node_id, poly in self.nav_polygons.items():
			color = active_poly_color if node_id in active_nodes else poly_color

			# Obtiene los puntos del contorno del polígono.
			puntos_contorno = list(poly.exterior.coords)
			# Ajusta la posición de cada punto del contorno según el desplazamiento de la cámara.
			puntos_ajustados = [(p[0] - camera_offset.x, p[1] - camera_offset.y) for p in puntos_contorno]
			# Dibuja el contorno del polígono con una línea cerrada de color rojo.
			pygame.draw.lines(surface, color, True, puntos_ajustados, 1)
		
		for id1, id2 in self.edges:
			start_pos = (self.nodes[id1][0] - camera_offset.x, self.nodes[id1][1] - camera_offset.y)
			end_pos = (self.nodes[id2][0] - camera_offset.x, self.nodes[id2][1] - camera_offset.y)
			if start_pos and end_pos:
				pygame.draw.line(surface, graph_color, start_pos, end_pos, 1)

		for node_id in self.nodes:
			pos = (self.nodes[node_id][0] - camera_offset.x, self.nodes[node_id][1] - camera_offset.y)
			if pos:
				pygame.draw.circle(surface, graph_color, (int(pos[0]), int(pos[1])), 2)

	def find_node_at_position(self, position, start_node_id=None):
		character_point = Point(position[0], position[1])

		if start_node_id is not None and start_node_id in self.nav_polygons:
			if self.nav_polygons[start_node_id].contains(character_point):
				return start_node_id

			queue = deque([start_node_id])
			visited = {start_node_id}

			while queue:
				current_id = queue.popleft()
				for neighbor_id in self.graph.get(current_id, []):
					if neighbor_id not in visited:
						visited.add(neighbor_id)
						if self.nav_polygons[neighbor_id].contains(character_point):
							return neighbor_id
						queue.append(neighbor_id)
		
		for node_id, polygon in self.nav_polygons.items():
			if polygon.contains(character_point):
				return node_id
		
		return None