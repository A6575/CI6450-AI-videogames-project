import heapq
import math
import pygame

# Heurística: Distancia Euclidiana
def heuristic(a, b):
	return math.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)

# Implementación A*
def a_star_search(start_node_id, goal_node_id, nodes, edges):
	graph = {node_id: [] for node_id in nodes}
	for id1, id2 in edges:
		graph[id1].append(id2)
		graph[id2].append(id1)

	open_set=[]
	heapq.heappush(open_set, (0, start_node_id))
	
	came_from = {}

	g_score = {node_id: float('inf') for node_id in nodes}
	g_score[start_node_id] = 0

	f_score = {node_id: float('inf') for node_id in nodes}
	f_score[start_node_id] = heuristic(nodes[start_node_id], nodes[goal_node_id])

	while open_set:
		_, current_id = heapq.heappop(open_set)

		if current_id == goal_node_id:
			path = []
			while current_id in came_from:
				path.append(current_id)
				current_id = came_from[current_id]
			path.append(start_node_id)
			return path[::-1]
		
		for neighbor_id in graph[current_id]:
			tentative_g_score = g_score[current_id] + heuristic(nodes[current_id], nodes[neighbor_id])

			if tentative_g_score < g_score[neighbor_id]:
				came_from[neighbor_id] = current_id
				g_score[neighbor_id] = tentative_g_score
				f_score[neighbor_id] = tentative_g_score + heuristic(nodes[neighbor_id], nodes[goal_node_id])
				if neighbor_id not in [i[1] for i in open_set]:
					heapq.heappush(open_set, (f_score[neighbor_id], neighbor_id))
		
	return None

def draw_path(surface, path, nodes, camera_offset, color=(0, 191, 255), width=3):
    """
    Dibuja una línea que representa el camino calculado por A*.
    """
    # Se asegura de que haya al menos dos puntos para dibujar una línea.
    if path and len(path) > 1:
        # Convierte la lista de IDs de nodos en una lista de puntos de coordenadas.
        path_points = [nodes[node_id] for node_id in path]
        
        # Ajusta los puntos del camino según el desplazamiento de la cámara.
        adjusted_points = [(p[0] - camera_offset.x, p[1] - camera_offset.y) for p in path_points]
        
        # Dibuja una serie de líneas conectadas que forman el camino.
        pygame.draw.lines(surface, color, False, adjusted_points, width)