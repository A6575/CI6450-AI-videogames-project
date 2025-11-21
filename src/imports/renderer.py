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
                # iterar sobre (x, y, gid)
                for x, y, image in layer.tiles():
                    if image:
                        self.screen.blit(image, (x * self.game_map.tmx_data.tilewidth - self.camera.left, 
                                                  y * self.game_map.tmx_data.tileheight - self.camera.top))

    def _draw_character(self, character):
        if hasattr(character, 'is_hit') and character.is_hit:
            # Si el personaje está en estado "hit", parpadea no dibujándolo en frames alternos.
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                return
        
        if hasattr(character, 'is_powered_up') and character.is_powered_up:
            if not character.aura_blinking or (pygame.time.get_ticks() // 200) % 2 == 0:
                aura_radius = character.sprite_size[0] * 0.7
                aura_color = (255, 0, 223)

                aura_surface = pygame.Surface((aura_radius * 2, aura_radius * 2), pygame.SRCALPHA)

                pygame.draw.circle(aura_surface, aura_color, (aura_radius, aura_radius), aura_radius)

                aura_surface.set_alpha(90)

                aura_pos_x = character.kinematic.position.x - self.camera.left
                aura_pos_y = character.kinematic.position.y - self.camera.top
                aura_rect = aura_surface.get_rect(center=(aura_pos_x, aura_pos_y))

                self.screen.blit(aura_surface, aura_rect)

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
        name_surface = self.font.render(character.name, True, (0, 0, 0))
        name_rect = name_surface.get_rect(center=(screen_pos_x, screen_pos_y - character.sprite_size[1] // 2 - 10))
        self.screen.blit(name_surface, name_rect)
    
    def _draw_obstacles(self):
        # Itera sobre todas las formas de colisión cargadas desde el mapa.
        for shape_type, shape_data in self.game_map.obstacles:
            if shape_type == 'rect':
                # Si la forma es un rectángulo.
                # Ajusta la posición del rectángulo a las coordenadas de la cámara.
                screen_rect = shape_data.move(-self.camera.left, -self.camera.top)
                # Dibuja el contorno del rectángulo en la pantalla.
                pygame.draw.rect(self.screen, (255, 0, 0), screen_rect, 1)
            elif shape_type == 'poly':
                # Si la forma es un polígono.
                # Ajusta las coordenadas de cada punto del polígono a la cámara.
                screen_points = [(p[0] - self.camera.left, p[1] - self.camera.top) for p in shape_data]
                # Dibuja el contorno del polígono en la pantalla.
                pygame.draw.polygon(self.screen, (255, 0, 0), screen_points, 1)

    def _draw_objects(self, honey_pots, power_ups, spider_webs, seed_projectiles, spider_projectiles):
        if spider_webs:
            for web in spider_webs:
                screen_rect = web.rect.move(-self.camera.left, -self.camera.top)
                self.screen.blit(web.image, screen_rect)

        if honey_pots:
            for pot in honey_pots:
                shadow_offset = (3, 3)
                shadow_rect = pot.rect.move(-self.camera.left + shadow_offset[0], -self.camera.top + shadow_offset[1])
                self.screen.blit(pot.shadow_surface, shadow_rect)
                screen_rect = pot.rect.move(-self.camera.left, -self.camera.top)
                self.screen.blit(pot.image, screen_rect)

        if power_ups:
            for power_up in power_ups:
                shadow_offset = (3, 3)
                shadow_rect = power_up.rect.move(-self.camera.left + shadow_offset[0], -self.camera.top + shadow_offset[1])
                self.screen.blit(power_up.shadow_surface, shadow_rect)
                screen_rect = power_up.rect.move(-self.camera.left, -self.camera.top)
                self.screen.blit(power_up.image, screen_rect)

        if seed_projectiles:
            for projectile in seed_projectiles:
                screen_rect = projectile.rect.move(-self.camera.left, -self.camera.top)
                self.screen.blit(projectile.image, screen_rect)

        if spider_projectiles:
            for projectile in spider_projectiles:
                screen_rect = projectile.rect.move(-self.camera.left, -self.camera.top)
                self.screen.blit(projectile.image, screen_rect)

    def draw(self, player, enemies, honey_pots=None, power_ups=None, spider_webs=None, seed_projectiles=None, spider_projectiles=None, show_debug=False):
        self.screen.fill((0, 0, 0)) # Black background
        self._draw_map()
        if show_debug:
            self._draw_obstacles()
        self._draw_character(player)
        self._draw_objects(honey_pots, power_ups, spider_webs, seed_projectiles, spider_projectiles)
        for enemy in enemies:
            self._draw_character(enemy)
