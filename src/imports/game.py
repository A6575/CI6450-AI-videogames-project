# Clase principal del juego que maneja la inicialización, el bucle principal y la integración de todos los componentes.
import pygame
import random
from pathlib import Path
from imports.renderer import Renderer
from imports.map.mapa import Map
from imports.map.obj_lists import HONEY_LIST
from imports.player.player import Player
from imports.scenario_factory import ScenarioFactory
from imports.pathfinding.a_star import a_star_search, draw_path
from imports.nav_mesh import NavMesh
from imports.objects.game_obj import HoneyPot, PowerUp, SpiderWeb, SeedProjectile
from imports.npc.hsm_data import build_tejedora_hsm, build_cazadora_hsm, build_criadora_hsm
from imports.npc.npc import NPC
from imports.tactical import TacticalManager

BASE_DIR = Path(__file__).resolve().parents[2]   # tres niveles arriba

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
            560,
            550,
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
        self.eggs = pygame.sprite.Group()

        self.show_loading_screen("Cargando Navigation Mesh...")

        try:
            self.nav_mesh = NavMesh(self.map.tmx_data)
            self._spawn_objects()
            self.tactical_manager = TacticalManager(self.nav_mesh, self.map.obstacles)
        except ValueError as e:
            print(e)
            self.nav_mesh = None
            self.tactical_manager = None
        
        self.clicked_node_ids = []
        
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
            
    def draw_player_lives(self):
        """
        Dibuja las vidas del jugador en la pantalla.
        """
        lives = [
            pygame.image.load(str(BASE_DIR / "assets" / "health" / "3-hearts.png")).convert_alpha(), # 3 vidas
            pygame.image.load(str(BASE_DIR / "assets" / "health" / "2-hearts.png")).convert_alpha(), # 2 vidas
            pygame.image.load(str(BASE_DIR / "assets" / "health" / "1-heart.png")).convert_alpha(),  # 1 vida
            pygame.image.load(str(BASE_DIR / "assets" / "health" / "0-heart.png")).convert_alpha(), # 0 vidas
        ]
        life_index = max(0, min(3, 3 - self.player.lives))  # Asegura que el índice esté entre 0 y 3
        life_image = lives[life_index]
        self.screen.blit(life_image, (self.screen.get_width() - life_image.get_width() - 10, 10))  # Dibuja en la esquina superior derecha con un margen de 10 píxeles

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

    def show_game_over_screen(self):
        pygame.time.delay(500)  # Pequeña pausa antes de mostrar la pantalla de Game Over
        self.screen.fill((20, 20, 40))
        font = pygame.font.SysFont('Arial', 50)
        text_surface = font.render("Game Over :(", True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(text_surface, text_rect)

        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
    
    def _spawn_objects(self):
        if not self.nav_mesh or not self.nav_mesh.nodes:
            return
        
        all_node_ids = set(self.nav_mesh.nodes.keys())
        possible_power_up_nodes = list(all_node_ids - set(HONEY_LIST))
        random.shuffle(possible_power_up_nodes)
        POWER_UP_LIST = possible_power_up_nodes[:5]  # Selecciona 5 nodos aleatorios para power-ups

        for node_id in HONEY_LIST:
            if not self.nav_mesh.nodes.get(node_id):
                break

            node_coords = self.nav_mesh.nodes[node_id]

            on_web = random.random() < 0.30

            pot = HoneyPot(node_coords[0], node_coords[1], node_id, on_web)
            self.honey_pots.add(pot)

            if on_web:
                web = SpiderWeb(node_coords[0], node_coords[1], node_id, has_pot=True)
                self.spider_webs.add(web)
        
        for node_id in POWER_UP_LIST:
            if not self.nav_mesh.nodes.get(node_id):
                break
            
            node_coords = self.nav_mesh.nodes[node_id]
            power_up = PowerUp(node_coords[0], node_coords[1], node_id)
            self.power_ups.add(power_up)
    
    def notify_alert(self, player_node_id, player_health):
        for enemy in self.enemies:
            if enemy.name in ["Cazadora", "Criadora"]:
                enemy.recive_alert(player_node_id, player_health)
                print(f"{enemy.name} ha sido alertado de la presencia del jugador en el nodo {player_node_id} con salud {player_health}.")
    
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
    
    def save_node_ids_to_file(self, filename):
        try:
            with open(filename, "w") as file:
                file.write(str(self.clicked_node_ids))
            print(f"IDs de nodos guardados en {filename}")
        except Exception as e:
            print(f"Error al guardar los IDs de nodos: {e}")
    
    def draw_honey_counter(self):
        """
        Dibuja el contador de tarros de miel recolectados en la pantalla.
        """
        # Texto descriptivo "Tarros de Miel"
        font = pygame.font.SysFont('Arial', 24)
        title_text = font.render("Tarros de Miel:", True, (0, 0, 0))  # Texto en negro
        title_rect = title_text.get_rect(topleft=(10, 10))  # Posición en la esquina superior izquierda
        self.screen.blit(title_text, title_rect)

        # Contador de tarros recolectados
        total_honey_pots = len(HONEY_LIST)
        counter_text = f"{self.player.honey_collected}/{total_honey_pots}"
        counter_surface = font.render(counter_text, True, (0, 0, 0))  # Texto en negro
        counter_rect = counter_surface.get_rect(topleft=(title_rect.right + 10, title_rect.top))
        self.screen.blit(counter_surface, counter_rect)
    
    def run(self, npc_type="No role"):
        self.spawn_enemy(npc_type, 50, 100)
        
        running = True
        show_nav_mesh = False
        dt = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    #self.save_node_ids_to_file("nodes_id.txt")
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
                        print(f"Clicked world position: {world_pos}, Goal node: {goal_node} ({self.nav_mesh.nodes.get(goal_node)})")
                        self.clicked_node_ids.append(goal_node)

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

            if self.tactical_manager:
                self.tactical_manager.update_influence_maps(self.honey_pots.sprites())
            
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
                self.eggs,
                show_debug = show_nav_mesh
            )

            """ if self.player.health <= 0:
                self.show_game_over_screen()
                running = False """

            if show_nav_mesh and self.nav_mesh:
                active_nodes = []
                if self.player.current_node_id is not None:
                    active_nodes.append(self.player.current_node_id)
                for enemy in self.enemies:
                    if enemy.current_node_id is not None:
                        active_nodes.append(enemy.current_node_id)

                """ self.nav_mesh.draw_nav_mesh(
                    self.screen,
                    self.renderer.camera,
                    self.tactical_manager.tactical_data if self.tactical_manager else None,
                    active_nodes=active_nodes
                ) """

                if self.test_path:
                    draw_path(
                        self.screen,
                        self.test_path,
                        self.nav_mesh.nodes,
                        self.renderer.camera,
                        color=(255, 0, 0),
                        width=4
                    )
                
                if self.tactical_manager:
                    self.tactical_manager.draw_debug(self.screen, self.renderer.camera)
                    self.tactical_manager.draw_debug_tactical_names(
                        self.screen, 
                        self.tactical_manager.tactical_data,
                        self.nav_mesh.nodes,
                        self.renderer.camera
                    )

            self.draw_honey_counter()
            self.draw_player_lives()
            pygame.display.flip()
            dt = self.clock.tick(60) / 1000
            
        pygame.quit()
