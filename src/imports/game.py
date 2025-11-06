# Clase principal del juego que maneja la inicialización, el bucle principal y la integración de todos los componentes.
import pygame
from imports.renderer import Renderer
from imports.map.mapa import Map
from imports.player.player import Player
from imports.scenario_factory import ScenarioFactory
from imports.nav_mesh import load_nav_mesh, draw_nav_mesh
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Bee-Collector")
        self.clock = pygame.time.Clock()
        self.map = Map('assets/mapa/mapa.tmx')
        self.renderer = Renderer(self.screen, self.map)
        self.player = Player(
            "Hero", 
            100, 
            self.screen.get_width() // 2 + 16,
            self.screen.get_height() // 2 + 16,
        )
        self.scenario_factory = ScenarioFactory(self.screen, self.map)
        self.enemies = []
        self.uses_rotation = False

        try:
            self.nav_nodes, self.nav_edges, self.nav_polygons = load_nav_mesh(self.map.tmx_data)
        except ValueError as e:
            print(e)
            self.nav_nodes, self.nav_edges, self.nav_polygons = {}, [], {}

    def run(self, scenario_type):
        self.enemies, self.uses_rotation = self.scenario_factory.create_scenario(scenario_type, self.player, None)
        
        running = True
        show_nav_mesh = False
        dt = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g:
                        show_nav_mesh = not show_nav_mesh
                        print(f"Nav mesh display toggled to {'ON' if show_nav_mesh else 'OFF'}")
            # Update player
            keys = pygame.key.get_pressed()
            # Se pasa la lista de obstáculos al método de movimiento del jugador.
            self.player.move(
                keys,
                pygame.math.Vector2(0,0),
                dt, 
                bounds=(self.map.width_pixels, self.map.height_pixels), 
                margin=(self.player.sprite_size[0] / 2, self.player.sprite_size[1] / 2),
                obstacles=self.map.obstacles
            )
            self.player.update_animation(dt)
            # Update enemies
            for enemy in self.enemies:
                enemy.update_with_algorithm(
                    dt, 
                    uses_rotation=self.uses_rotation,
                    bounds=(self.map.width_pixels, self.map.height_pixels),
                    margin=(enemy.sprite_size[0] / 2, enemy.sprite_size[1] / 2),
                    obstacles=self.map.obstacles
                )
                enemy.update_animation(dt)

            # Update camera
            self.renderer.update_camera(self.player)

            # Render everything
            self.renderer.draw(self.player, self.enemies)
            if show_nav_mesh:
                draw_nav_mesh(self.screen, self.nav_nodes, self.nav_edges, self.nav_polygons, self.renderer.camera)

            pygame.display.flip()
            dt = self.clock.tick(60) / 1000
            
        pygame.quit()
