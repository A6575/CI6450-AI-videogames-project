import pygame
import math

COVER_POINTS = [1432, 677, 709, 614, 806, 804, 1296, 1217, 1228, 1238, 765, 700, 828, 766, 1433, 829, 831, 1434, 967, 1406, 1445, 952, 954, 1013, 1075, 1076, 1074, 1356, 1322, 1398, 1399, 1109, 1411, 1386, 1385, 1384, 1286, 1474, 1049, 1043, 1044, 1037, 1031, 1032, 1023]
CORNER_POINTS = [1432, 806, 804, 802, 1296, 710, 681, 682, 700, 765, 1217, 1228, 766, 831, 1433, 829, 677, 709, 1386, 1296, 1322, 1356, 1115, 1398, 1399, 1406, 1445, 952, 954, 1434, 967, 1013, 1076, 1454, 1452]
CROSS_ROAD_POINTS = [1247, 1463, 1257, 1429, 1460, 1410, 1159, 945, 997, 837, 644, 675]

class TacticalInfo:
    """
    Clase contenedora para la información táctica extra que se asocia a un nodo existente.
    No contiene posición ni ID, ya que eso lo maneja el NavMesh.
    """
    def __init__(self, is_cover=0, is_corner=0, is_crossroad=0):
        # Cualidades Dinámicas (Se actualizan en cada frame)
        self.honey_amount = 0.0      # Cantidad de miel en este nodo (si aplica)
        
        # Cualidades Estáticas (Se calculan una vez al inicio)
        self.is_cover = is_cover     # True si el nodo ofrece cobertura (cerca de obstáculo)
        self.is_corner = is_corner   # True si el nodo está en una esquina (pocas conexiones)
        self.is_crossroad = is_crossroad # True si el nodo es un cruce (muchas conexiones en diferentes direcciones)

class TacticalManager:
    """
    Gestor de inteligencia táctica.
    En lugar de crear nodos nuevos, analiza los nodos del NavMesh existente
    y mantiene un registro paralelo de su información táctica.
    """
    def __init__(self, nav_mesh, obstacles):
        self.nav_mesh = nav_mesh
        self.obstacles = obstacles
        
        # Diccionario que mapea: ID_del_Nodo (int) -> TacticalInfo (obj)
        self.tactical_data = {} 
        
        # Analizar el mapa una sola vez al inicio (Cualidades Estáticas)
        self._analyze_existing_nodes()

    def _analyze_existing_nodes(self):
        """
        Recorre todos los nodos del NavMesh y determina sus cualidades estáticas
        (como si sirven de cobertura).
        """
        if not self.nav_mesh or not self.nav_mesh.nodes:
            return

        for node_id, coords in self.nav_mesh.nodes.items():
            x, y = coords
            
            is_cover = 1 if node_id in COVER_POINTS else 0
            # Analisis de Conexiones
            connections = self.nav_mesh.graph.get(node_id, [])
            is_crossroad = 1 if node_id in CROSS_ROAD_POINTS else 0

            # Analisis de Esquina (menos de 4 conexiones)
            is_corner = 1 if node_id in set(CORNER_POINTS) else 0
            # Analisis de Alta Conectividad (5 o más conexiones)

            # Guardamos la metadata asociada a este ID
            self.tactical_data[node_id] = TacticalInfo(
                is_cover=is_cover, 
                is_corner=is_corner, 
                is_crossroad=is_crossroad,
            )

    def update_influence_maps(self, honey_pots):
        """
        Actualiza los mapas de influencia en función de los tarros de miel.
        Cada nodo recibe un valor de influencia basado en la proximidad a los tarros de miel.
        
        :param honey_pots: Lista de objetos HoneyPot en el juego.
        """
        if not self.nav_mesh or not self.nav_mesh.nodes:
            return

        # Reinicia la influencia de miel en todos los nodos
        for node_id, info in self.tactical_data.items():
            info.honey_amount = 0.0

        # Calcula la influencia de miel para cada nodo
        for pot in honey_pots:
            pot_pos = pygame.math.Vector2(pot.initial_pos)

            for node_id, coords in self.nav_mesh.nodes.items():
                node_pos = pygame.math.Vector2(coords[0], coords[1])
                
                # Distancia entre el nodo y el tarro de miel
                dist_to_pot = node_pos.distance_to(pot_pos)
                
                # Influencia basada en la distancia (inversa: más cerca = más influencia)
                if dist_to_pot < 50 and dist_to_pot > 0:  # Umbral de influencia (50 px)
                    influence = max(0, 50 - dist_to_pot)
                    self.tactical_data[node_id].honey_amount += influence
    
    def draw_debug_tactical_names(self, surface, tactical_data, nodes, camera_offset):
        font = pygame.font.SysFont(None, 14)
        for node_id, info in tactical_data.items():
            # Construir el nombre dinámico basado en las cualidades tácticas del nodo
            name_parts = []
            if info.honey_amount > 0:
                name_parts.append("honey")
            if info.is_corner == 1:
                name_parts.append("corner")
            if info.is_cover == 1:
                name_parts.append("cover")
            if info.is_crossroad == 1:
                name_parts.append("crossroad")
            
            # Si no hay cualidades, no dibujar nada
            if not name_parts:
                continue
            
            # Generar el texto final
            node_name = ", ".join(name_parts)
            
            # Obtener la posición ajustada del nodo
            node_pos = nodes[node_id]
            adjusted_pos = (node_pos[0] - camera_offset.x, node_pos[1] - camera_offset.y)
            
            # Renderizar el texto
            text_surface = font.render(node_name, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=adjusted_pos)  # Centrar el texto en el nodo
            
            # Dibujar el texto centrado
            surface.blit(text_surface, text_rect)

    def draw_debug(self, surface, camera):
        """Dibuja información táctica sobre los nodos existentes."""
        font = pygame.font.SysFont('Arial', 10)
        
        for node_id, info in self.tactical_data.items():
            coords = self.nav_mesh.nodes[node_id]
            screen_x = coords[0] - camera.x
            screen_y = coords[1] - camera.y

            
            radius = 4
            if info.is_cover == 1:
                # Anillo morado si es cobertura
                pygame.draw.circle(surface, (128, 0, 128), (screen_x, screen_y), radius + 2, 2)
            if info.is_corner == 1:
                # Anillo negro si es esquina
                pygame.draw.circle(surface, (0, 0, 0), (screen_x, screen_y), radius + 4, 1)
            if info.is_crossroad == 1:
                # Anillo rojo si es área abierta
                pygame.draw.circle(surface, (255, 0, 0), (screen_x, screen_y), radius + 6, 1)
            if info.honey_amount > 0:
                pygame.draw.circle(surface, (0, 255, 0), (screen_x, screen_y), radius)