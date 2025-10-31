# src/map.py

import pygame
import pytmx

class Map:
    def __init__(self, tmx_file):
        self.tmx_data = pytmx.load_pygame(tmx_file, pixelalpha=True)
        self.width_pixels = self.tmx_data.width * self.tmx_data.tilewidth
        self.height_pixels = self.tmx_data.height * self.tmx_data.tileheight
        self.obstacles = []
        self._load_obstacles()

    def _load_obstacles(self):
        for obj in self.tmx_data.objects:
            if obj.type == 'obstacle':
                self.obstacles.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
