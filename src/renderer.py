# src/renderer.py

import pygame
import pytmx

class Renderer:
    def __init__(self, screen, game_map):
        self.screen = screen
        self.game_map = game_map
        self.camera = pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height())
        self.font = pygame.font.SysFont(None, 16)

    def update_camera(self, target):
        self.camera.center = target.kinematic.position
        self.camera.left = max(0, self.camera.left)
        self.camera.right = min(self.game_map.width_pixels, self.camera.right)
        self.camera.top = max(0, self.camera.top)
        self.camera.bottom = min(self.game_map.height_pixels, self.camera.bottom)

    def _draw_map(self):
        for layer in self.game_map.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                # Use tiles() to iterate over (x, y, gid) to avoid issues with type checkers
                for x, y, image in layer.tiles():
                    if image:
                        self.screen.blit(image, (x * self.game_map.tmx_data.tilewidth - self.camera.left, 
                                                  y * self.game_map.tmx_data.tileheight - self.camera.top))

    def _draw_character(self, character):
        # Escalar la sombra y rotarla
        shadow_scaled = pygame.transform.scale(character.shadow_surface, character.sprite_size)
        rotated_shadow = pygame.transform.rotate(shadow_scaled, character.kinematic.orientation)
        
        # Ajustar la posición de la sombra en la pantalla (con un pequeño desfase)
        shadow_offset = (5, 5) # Desfase en X e Y para que la sombra aparezca debajo y a la derecha
        shadow_pos_x = character.kinematic.position.x - self.camera.left + shadow_offset[0]
        shadow_pos_y = character.kinematic.position.y - self.camera.top + shadow_offset[1]
        shadow_rect = rotated_shadow.get_rect(center=(shadow_pos_x, shadow_pos_y))
        
        # Dibujar la sombra en la pantalla
        self.screen.blit(rotated_shadow, shadow_rect)
        
        # Escalar png y rotar segun orientacion
        sprite_grande = pygame.transform.scale(character.sprite, character.sprite_size)
        rotated_sprite = pygame.transform.rotate(sprite_grande, character.kinematic.orientation)
        
        # Adjust position based on camera
        screen_pos_x = character.kinematic.position.x - self.camera.left
        screen_pos_y = character.kinematic.position.y - self.camera.top
        
        rect = rotated_sprite.get_rect(center=(screen_pos_x, screen_pos_y))
        self.screen.blit(rotated_sprite, rect)

        # Mostrar nombre arriba del personaje
        name_surface = self.font.render(character.name, True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(screen_pos_x, screen_pos_y - character.sprite_size[1] // 2 - 10))
        self.screen.blit(name_surface, name_rect)

    def draw(self, player, enemies):
        self.screen.fill((0, 0, 0)) # Black background
        self._draw_map()
        self._draw_character(player)
        for enemy in enemies:
            self._draw_character(enemy)
