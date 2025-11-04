# src/map.py
import pygame
import pytmx
from typing import Any, cast  # Importación para permitir cast a Any y evitar errores de tipado

class Map:
    def __init__(self, tmx_file):
        self.tmx_data = pytmx.load_pygame(tmx_file, pixelalpha=True)
        self.width_pixels = self.tmx_data.width * self.tmx_data.tilewidth
        self.height_pixels = self.tmx_data.height * self.tmx_data.tileheight
        self.obstacles = []
        self._load_walls_and_obstacles()

    def _load_walls_and_obstacles(self):
        # --- Procesar colisionadores ---
        # Busca el índice de la capa llamada "walls" (donde están los tiles de colisión)
        walls_layer = None
        for i, layer in enumerate(self.tmx_data.layers):
            if hasattr(layer, 'name') and layer.name == "estructuras":
                walls_layer = i

        if walls_layer is None:
            raise Exception("No se encontró la capa 'walls' en el mapa.")
        
        colliders_gen = self.tmx_data.get_tile_colliders()
        colliders_list = list(colliders_gen)

        # Para cada tile del tileset que tiene colisionador (objectgroup)
        for i, (tile_id_local, obj_group) in enumerate(colliders_list):
            if obj_group is not None:
                for obj in obj_group:
                    # Recorre todo el mapa buscando las posiciones donde ese tile está colocado
                    for y in range(self.tmx_data.height):
                        for x in range(self.tmx_data.width):
                            gid = self.tmx_data.get_tile_gid(x, y, walls_layer)
                            # Si el GID del tile en el mapa coincide con el tile_id_local del colisionador
                            if gid == tile_id_local:
                                # Se realiza un cast a Any para evitar errores de tipado
                                obj_any = cast(Any, obj)
                                
                                # Calcula la posición base del tile en el mapa (en píxeles)
                                tile_base_x = x * self.tmx_data.tilewidth
                                tile_base_y = y * self.tmx_data.tileheight

                                # Verifica si el objeto de colisión es un polígono
                                if hasattr(obj_any, 'points'):
                                    # Es un polígono (como un triángulo).
                                    # Calcula las coordenadas absolutas de cada punto del polígono.
                                    points = [
                                        (int(tile_base_x + p[0]), int(tile_base_y + p[1]))
                                        for p in obj_any.points
                                    ]
                                    # Almacena el tipo de forma y la lista de puntos.
                                    self.obstacles.append(('poly', points))
                                else:
                                    # Es un rectángulo.
                                    # Crea el rectángulo de colisión en coordenadas absolutas.
                                    rect = pygame.Rect(
                                        int(tile_base_x + obj_any.x),
                                        int(tile_base_y + obj_any.y),
                                        int(obj_any.width),
                                        int(obj_any.height)
                                    )
                                    # Almacena el tipo de forma y el objeto Rect.
                                    self.obstacles.append(('rect', rect))
