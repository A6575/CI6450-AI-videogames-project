# Clase principal del juego que maneja la inicialización, el bucle principal y la integración de todos los componentes.
import pygame
from renderer import Renderer
from mapa import Map
from imports.player.player import Player
from scenario_factory import ScenarioFactory

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Juego IA con Tilemap")
        self.clock = pygame.time.Clock()
        self.map = Map('assets/mapa/mapa.tmx')
        self.renderer = Renderer(self.screen, self.map)
        self.player = Player(
            "Hero", 
            100, 
            self.screen.get_width() // 2,
            self.screen.get_height() // 2,
        )
        self.scenario_factory = ScenarioFactory(self.screen, self.map)
        self.enemies = []
        self.uses_rotation = False

    def run(self, scenario_type):
        self.enemies, self.uses_rotation = self.scenario_factory.create_scenario(scenario_type, self.player)
        
        running = True
        dt = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Update player
            keys = pygame.key.get_pressed()
            self.player.move(keys, pygame.math.Vector2(0, 0), dt, bounds=(self.map.width_pixels, self.map.height_pixels), margin=(self.player.sprite_size[0] / 2, self.player.sprite_size[1] / 2))
            self.player.update_animation(dt)
            # Update enemies
            for enemy in self.enemies:
                enemy.update_with_algorithm(
                    dt, 
                    uses_rotation=self.uses_rotation,
                    bounds=(self.map.width_pixels, self.map.height_pixels),
                    margin=(enemy.sprite_size[0] / 2, enemy.sprite_size[1] / 2)
                )
                enemy.update_animation(dt)

            # Update camera
            self.renderer.update_camera(self.player)

            # Render everything
            self.renderer.draw(self.player, self.enemies)

            pygame.display.flip()
            dt = self.clock.tick(60) / 1000
            
        pygame.quit()
