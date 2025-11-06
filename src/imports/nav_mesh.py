from shapely.geometry import Polygon, Point
import pygame

def load_nav_mesh(mapa_tmx):
	nav_polygons = {}
	nodes = {}

	for layer in mapa_tmx.layers:
		if layer.name == "nav_mesh":
			for obj in layer:
				if obj.type != "nodes":
					continue

				abs_points = []
				if hasattr(obj, 'points'):
					abs_points = [(point[0], point[1]) for point in obj.points]
				
				if not abs_points:
					continue

				polygon = Polygon(abs_points)
				nav_polygons[obj.id] = polygon

				centroid = polygon.centroid
				nodes[obj.id] = (centroid.x, centroid.y)
	
	if not nav_polygons:
		raise ValueError("Navigation mesh layer 'nav_mesh' not found in the TMX file.")

	edges = []
	polygon_ids = list(nav_polygons.keys())

	for i in range(len(polygon_ids)):
		for j in range(i + 1, len(polygon_ids)):
			poly1 = nav_polygons[polygon_ids[i]]
			poly2 = nav_polygons[polygon_ids[j]]

			# Primero, se comprueba si los polígonos se intersectan.
			if poly1.intersects(poly2):
				# Se calcula la geometría de la intersección.
				intersection = poly1.intersection(poly2)
				# Se considera una arista válida si la intersección tiene una longitud mayor que cero.
				# Esto funciona para LineString (unión perfecta) y para pequeños polígonos de superposición,
				# pero ignora las uniones de un solo punto (que tienen longitud cero).
				if intersection.length > 0:
					edges.append((polygon_ids[i], polygon_ids[j]))

	return nodes, edges, nav_polygons

def draw_nav_mesh(surface, nodes, edges, polygons, camera_offset=(0, 0), active_nodes=None, graph_color=(0, 0, 255), poly_color=(150, 150, 150), active_poly_color=(0,255,0)):
	if active_nodes is None:
		active_nodes = []
	
	# Itera sobre cada polígono que Shapely ha generado.
	for node_id, poly in polygons.items():
		color = active_poly_color if node_id in active_nodes else poly_color

		# Obtiene los puntos del contorno del polígono.
		puntos_contorno = list(poly.exterior.coords)
		# Ajusta la posición de cada punto del contorno según el desplazamiento de la cámara.
		puntos_ajustados = [(p[0] - camera_offset.x, p[1] - camera_offset.y) for p in puntos_contorno]
		# Dibuja el contorno del polígono con una línea cerrada de color rojo.
		pygame.draw.lines(surface, color, True, puntos_ajustados, 1)
	
	for id1, id2 in edges:
		start_pos = (nodes[id1][0] - camera_offset.x, nodes[id1][1] - camera_offset.y)
		end_pos = (nodes[id2][0] - camera_offset.x, nodes[id2][1] - camera_offset.y)
		if start_pos and end_pos:
			pygame.draw.line(surface, graph_color, start_pos, end_pos, 1)

	for node_id in nodes:
		pos = (nodes[node_id][0] - camera_offset.x, nodes[node_id][1] - camera_offset.y)
		if pos:
			pygame.draw.circle(surface, graph_color, (int(pos[0]), int(pos[1])), 3)

def find_node_at_position(position, nav_polygons):
	character_point = Point(position[0], position[1])

	for node_id, polygon in nav_polygons.items():
		if polygon.contains(character_point):
			return node_id
	return None