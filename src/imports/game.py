# Clase principal del juego que maneja la inicialización, el bucle principal y la integración de todos los componentes.
import pygame
import random
from imports.renderer import Renderer
from imports.map.mapa import Map
from imports.player.player import Player
from imports.scenario_factory import ScenarioFactory
from imports.pathfinding.a_star import a_star_search, draw_path
from imports.nav_mesh import NavMesh
from imports.objects.game_obj import HoneyPot, PowerUp, SpiderWeb, SeedProjectile
from imports.npc.hsm_data import build_tejedora_hsm, build_cazadora_hsm, build_criadora_hsm
from imports.npc.npc import NPC
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

        self.honey_pots = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        self.spider_webs = pygame.sprite.Group()
        self.seed_projectiles = pygame.sprite.Group()
        self.spider_projectiles = pygame.sprite.Group()

        self.show_loading_screen("Cargando Navigation Mesh...")

        try:
            self.nav_mesh = NavMesh(self.map.tmx_data)
            self._spawn_objects()
        except ValueError as e:
            print(e)
            self.nav_mesh = None
        
        
    def spawn_enemy(self, enemy_type, x, y):
        enemy = None
        if enemy_type == "Tejedora":
            enemy = NPC("Tejedora", 100, x, y, algorithm_name="")
            enemy.current_node_id = self.nav_mesh.find_node_at_position(enemy.kinematic.position, enemy.current_node_id)#type:ignore
            enemy.init_hsm(build_tejedora_hsm, self)
        elif enemy_type == "Cazadora":
            enemy = NPC("Cazadora", 100, x, y, algorithm_name="")
            enemy.current_node_id = self.nav_mesh.find_node_at_position(enemy.kinematic.position, enemy.current_node_id)#type:ignore
            enemy.init_hsm(build_cazadora_hsm, self)
        elif enemy_type == "Criadora":
            enemy = NPC("Criadora", 100, x, y, algorithm_name="")
            enemy.current_node_id = self.nav_mesh.find_node_at_position(enemy.kinematic.position, enemy.current_node_id)#type:ignore
            enemy.init_hsm(build_criadora_hsm, self)
        else:
            self.enemies, self.uses_rotation = self.scenario_factory.create_scenario("DynamicArrive", self.player, None)
        
        if enemy and self.nav_mesh:
            self.enemies.append(enemy)

    def show_loading_screen(self, message):
        self.screen.fill((20, 20, 40))
        # Configura la fuente para el mensaje.
        font = pygame.font.SysFont('Arial', 30)
        text_surface = font.render(message, True, (255, 255, 255))
        
        # Centra el texto en la pantalla.
        text_rect = text_surface.get_rect(center=self.screen.get_rect().center)
        
        # Dibuja el texto en la pantalla.
        self.screen.blit(text_surface, text_rect)
        
        # Actualiza la pantalla para que el mensaje sea visible.
        pygame.display.flip()
        
    def _spawn_objects(self):
        if not self.nav_mesh or not self.nav_mesh.nodes:
            return
        
        possible_node_ids = list(self.nav_mesh.nodes.keys())
        random.shuffle(possible_node_ids)

        num_honey_pots = 10
        for _ in range(num_honey_pots):
            if not possible_node_ids:
                break

            node_id = possible_node_ids.pop()
            node_coords = self.nav_mesh.nodes[node_id]

            on_web = random.random() < 0.30

            pot = HoneyPot(node_coords[0], node_coords[1], node_id, on_web)
            self.honey_pots.add(pot)

            if on_web:
                web = SpiderWeb(node_coords[0], node_coords[1], node_id, has_pot=True)
                self.spider_webs.add(web)
        
        num_power_ups = 3
        for _ in range(num_power_ups):
            if not possible_node_ids:
                break
            
            node_id = possible_node_ids.pop()
            node_coords = self.nav_mesh.nodes[node_id]
            power_up = PowerUp(node_coords[0], node_coords[1], node_id)
            self.power_ups.add(power_up)
    
    def _handle_collisions(self):
        for pot in self.honey_pots.sprites():
            if self.player.rect.colliderect(pot.rect):
                self.player.honey_collected +=1
                if pot.on_web:
                    for web in self.spider_webs.sprites():
                        if web.has_pot and web.rect.colliderect(pot.rect):
                            web.has_pot = False
                            break
                print(f"Miel recolectada! Total: {self.player.honey_collected}")
                pot.kill()
        
        for power_up in self.power_ups.sprites():
            if self.player.rect.colliderect(power_up.rect):
                self.player.activate_power_up(power_up.duration)
                print("¡Poder recogido!")
                power_up.kill()

        enemies_to_remove = []

        for projectile in self.seed_projectiles:
            # Itera sobre cada enemigo en la lista de enemigos.
            for enemy in self.enemies:
                # Comprueba si el rectángulo del proyectil colisiona con el del enemigo.
                if projectile.rect.colliderect(enemy.rect) and not enemy.is_hit:
                    # Elimina el proyectil del grupo.
                    projectile.kill()
                    print("¡Enemigo alcanzado!")
                    if enemy.take_damage(projectile.damage):
                        print(f"{enemy.name} ha sido derrotado.")
                        enemies_to_remove.append(enemy)
                    # Rompe el bucle interno, ya que el proyectil ya impactó.
                    break
        
        # Elimina a los enemigos alcanzados de la lista principal de enemigos.
        if enemies_to_remove:
            self.enemies = [enemy for enemy in self.enemies if enemy not in enemies_to_remove]
    
    def run(self, scenario_type):
        self.spawn_enemy("Criadora", 50, 100)
        
        running = True
        show_nav_mesh = False
        dt = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # Activar navigation meshe
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g:
                        show_nav_mesh = not show_nav_mesh
                        print(f"Nav mesh display toggled to {'ON' if show_nav_mesh else 'OFF'}")
                    elif event.key == pygame.K_SPACE:
                        attack_data = self.player.attack()
                        if attack_data:
                            start_pos, direction = attack_data
                            self.seed_projectiles.add(SeedProjectile(start_pos[0], start_pos[1], direction))
                # Desactivar roles/algoritmos predefinidos en los NPC y pasar a usar unicamente PathFinding y
                # FollowPath
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

            self.honey_pots.update(dt)
            self.power_ups.update(dt)
            self.spider_webs.update(dt)
            self.seed_projectiles.update(dt)
            self.spider_projectiles.update(dt)
            # Actualizar jugador
            keys = pygame.key.get_pressed()
            # Se pasa la lista de obstáculos al método de movimiento del jugador.
            self.player.move(
                keys,
                pygame.math.Vector2(0,0),
                dt, 
                bounds=(self.map.width_pixels, self.map.height_pixels), 
                margin=(self.player.sprite_size[0] / 2, self.player.sprite_size[1] / 2),
                obstacles=self.map.obstacles,
                nav_mesh=self.nav_mesh,
                spider_webs=self.spider_webs
            )
            self.player.update_animation(dt)
            self.player.update(dt)

            self._handle_collisions()
            # Actualizar enemigos
            for enemy in self.enemies:
                if enemy.name == "DynamicArrive":
                    enemy.update_with_algorithm(
                        dt,
                        uses_rotation=self.uses_rotation,
                        bounds=(self.map.width_pixels, self.map.height_pixels),
                        margin=(enemy.sprite_size[0] // 2, enemy.sprite_size[1] // 2),
                        obstacles=self.map.obstacles,
                        nav_mesh=self.nav_mesh
                    )
                enemy.update_animation(dt)
                enemy.update(dt)

            # Actualizar cámara
            self.renderer.update_camera(self.player)

            # Renderizar todo
            self.renderer.draw(
                self.player, 
                self.enemies,
                self.honey_pots,
                self.power_ups,
                self.spider_webs,
                self.seed_projectiles,
                self.spider_projectiles,
                show_debug = show_nav_mesh
            )
            
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
