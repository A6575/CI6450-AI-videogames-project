# Clase principal del juego que maneja la inicialización, el bucle principal y la integración de todos los componentes.
import pygame
from imports.renderer import Renderer
from imports.map.mapa import Map
from imports.player.player import Player
from imports.scenario_factory import ScenarioFactory
from imports.pathfinding.a_star import a_star_search, draw_path
from imports.nav_mesh import NavMesh
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
        self.test_path = []

        try:
            self.nav_mesh = NavMesh(self.map.tmx_data)
        except ValueError as e:
            print(e)
            self.nav_mesh = None

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
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and self.enemies and self.nav_mesh:  # Left click
                        mouse_pos = pygame.mouse.get_pos()
                        world_pos = (mouse_pos[0] + self.renderer.camera.x, mouse_pos[1] + self.renderer.camera.y)
                        
                        seeker = self.enemies[0]

                        start_node = seeker.current_node_id
                        goal_node = self.nav_mesh.find_node_at_position(world_pos)

                        if start_node is not None and goal_node is not None and start_node != goal_node:
                            print(f"Buscando camino desde el nodo {start_node} al nodo {goal_node}...")
                            path_node_ids = a_star_search(start_node, goal_node, self.nav_mesh.nodes, self.nav_mesh.edges)
                            if path_node_ids:
                                print("¡Camino encontrado!", path_node_ids)
                                self.test_path = path_node_ids
                                seeker.follow_path_from_nodes(
                                    path_node_ids,
                                    self.nav_mesh.nodes,
                                    explicit_target=Player("Target", 0, world_pos[0], world_pos[1])
                                )
                            else:
                                print("No path found between the selected nodes.")
                                self.test_path = []
            # Update player
            keys = pygame.key.get_pressed()
            # Se pasa la lista de obstáculos al método de movimiento del jugador.
            self.player.move(
                keys,
                pygame.math.Vector2(0,0),
                dt, 
                bounds=(self.map.width_pixels, self.map.height_pixels), 
                margin=(self.player.sprite_size[0] / 2, self.player.sprite_size[1] / 2),
                obstacles=self.map.obstacles,
                nav_mesh=self.nav_mesh
            )
            self.player.update_animation(dt)
            # Update enemies
            for enemy in self.enemies:
                enemy.update_with_algorithm(
                    dt, 
                    uses_rotation=self.uses_rotation,
                    bounds=(self.map.width_pixels, self.map.height_pixels),
                    margin=(enemy.sprite_size[0] / 2, enemy.sprite_size[1] / 2),
                    obstacles=self.map.obstacles,
                    nav_mesh=self.nav_mesh
                )
                enemy.update_animation(dt)

            # Update camera
            self.renderer.update_camera(self.player)

            # Render everything
            self.renderer.draw(self.player, self.enemies)
            
            if show_nav_mesh and self.nav_mesh:
                active_nodes = []
                if self.player.current_node_id is not None:
                    active_nodes.append(self.player.current_node_id)
                for enemy in self.enemies:
                    if enemy.current_node_id is not None:
                        active_nodes.append(enemy.current_node_id)

                self.nav_mesh.draw_nav_mesh(
                    self.screen,
                    self.renderer.camera,
                    active_nodes=active_nodes
                )

                if self.test_path:
                    draw_path(
                        self.screen,
                        self.test_path,
                        self.nav_mesh.nodes,
                        self.renderer.camera,
                        color=(255, 0, 0),
                        width=4
                    )

            pygame.display.flip()
            dt = self.clock.tick(60) / 1000
            
        pygame.quit()
