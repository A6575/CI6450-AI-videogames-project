import time
import pygame
from pygame.image import load
from pygame.math import Vector2
from pygame import BLEND_RGBA_MULT
from pathlib import Path
from imports.moves.kinematic import Kinematic
from imports.moves.switcher import SWITCHER_ALGORITHMS
from imports.map.path import AStarPath
from imports.moves.path_following import FollowPath
from imports.npc.hsm_data import Context as HSMContext
from imports.objects.game_obj import SpiderProjectile

# Directorio base para cargar recursos
BASE_DIR = Path(__file__).resolve().parents[3]   # cuatro niveles arriba

class NPC:
	def __init__(self, name, health, x, y, algorithm_name=""):
		self.name = name				# Nombre del NPC
		self.health = health			# Salud del NPC
		self.is_hit = False
		self.hit_timer = 0.0
		self.hit_duration = 500
		self.kinematic = Kinematic(		# Estado cinemático del NPC
			position=Vector2(x, y),
			velocity=Vector2(0, 0), 
			orientation=270, 
			rotation=0
		)
		self.algorithm_name = algorithm_name	# Nombre del algoritmo de movimiento
		self.algorithm_class = None
		self.algorithm_params = {}
		self.algorithm_instance = None
		self.map_width = 800   # valores por defecto de tamaño del mapa
		self.map_height = 600
		# Rutas a las imágenes de las animaciones del NPC
		self.animation_paths = {
			"walk": [
				str(BASE_DIR / "assets" / "enemy" / "SpiderWalkingUp1.png"),
				str(BASE_DIR / "assets" / "enemy" / "SpiderWalkingUp2.png"),
				str(BASE_DIR / "assets" / "enemy" / "SpiderWalkingUp3.png"),
				str(BASE_DIR / "assets" / "enemy" / "SpiderWalkingUp4.png"),
			],
			"idle": [
				str(BASE_DIR / "assets" / "enemy" / "SpiderIdleUp1.png"),
				str(BASE_DIR / "assets" / "enemy" / "SpiderIdleUp2.png"),
				str(BASE_DIR / "assets" / "enemy" / "SpiderIdleUp3.png"),
				str(BASE_DIR / "assets" / "enemy" / "SpiderIdleUp4.png"),
			]
		}
		# Cargar las superficies de Pygame para cada animación
		self.animations = {
			"walk": [load(img).convert_alpha() for img in self.animation_paths["walk"]],
			"idle": [load(img).convert_alpha() for img in self.animation_paths["idle"]]
		}
		
		# --- Variables de control de animación ---
		self.current_animation = "walk" # Animación actual, por defecto 'walk'
		self.current_frame_index = 0 # Índice del fotograma actual
		self.sprite = self.animations[self.current_animation][self.current_frame_index] # Sprite actual
		self.sprite_size = (35, 35)
		self.rect = self.sprite.get_rect(center=(x, y))
		self.animation_timer = 0.0 # Temporizador para cambiar de fotograma
		self.animation_speed = 0.1 # Tiempo en segundos que dura cada fotograma

		# Crear una superficie para la sombra del mismo tamaño que el sprite original
		self.shadow_surface = self.sprite.copy()
		# Rellenar la superficie de la sombra con un color negro semi-transparente
		self.shadow_surface.fill((0, 0, 0, 100), special_flags=BLEND_RGBA_MULT)
		self.current_node_id = None
		self.hsm = None
		self.hsm_goal = None
		self._alert_started_at =  0.0
		self.attack_cooldown = 3.0
		self._last_attack_time = 0.0
		self._steal_in_progress = False
		self._steal_started_at = None
		self._has_stolen = False
		self._flee_started_at = None
		self._flee_duration = 0.0
		self._egg_laid = False
		self._egg_lay_started_at = None
		self._egg_lay_duration = 0.0

	def init_hsm(self, hsm_builder, game_world):
		ctx = HSMContext(self, game_world)
		self.hsm = hsm_builder(ctx)
	
	def emit_hsm_event(self, event: str):
		if self.hsm:
			return self.hsm.handle_event(event)
		return False
	
	def perform_throw_net(self, world):
		now = time.time()
		if now - self._last_attack_time < self.attack_cooldown:
			return False
		target = None
		if world and hasattr(world, 'player') and getattr(world.player, 'kinematic', None):
			target_pos = world.player.kinematic.position
			target = (target_pos.x, target_pos.y)
		
		if not target:
			return False
		
		pos = self.kinematic.position
		origin =  Vector2(pos.x, pos.y)
		target = Vector2(target)
		dir_vec = (target - origin)
		
		if dir_vec.length() == 0:
			dir_vec = Vector2(1, 0)
		else:
			dir_vec = dir_vec.normalize()
		
		proj = SpiderProjectile(origin.x, origin.y, dir_vec, owner=self)
		if world is not None:
			proj.world = world
		if world and hasattr(world, 'spider_projectiles'):
			world.spider_projectiles.add(proj)
		self._last_attack_time = now
		self.is_attacking = True
		self._attack_started_at = now
		return True
	
	def can_throw_net(self):
		now = time.time()
		return (now - self._last_attack_time) >= self.attack_cooldown

	def take_damage(self, amount):
		if not self.is_hit:
			self.health -= amount
			self.is_hit = True
			self.hit_timer = pygame.time.get_ticks()
			print(f"{self.name} fue golpeado y recibió {amount} de daño. Vida restante: {self.health}")
			return self.health <= 0
		return False
	
	def update(self, dt):
		if self.is_hit and pygame.time.get_ticks() - self.hit_timer > self.hit_duration:
			self.is_hit = False
		
		if hasattr(self, 'hsm') and self.hsm:
			self.hsm.update(dt)
	
	def follow_path_from_nodes(self, path_nodes, nav_mesh_nodes, explicit_target):
		path_points = [Vector2(nav_mesh_nodes[node_id]) for node_id in path_nodes]

		if len(path_points) < 2:
			self.set_algorithm()
			return
		
		astar_path_instance = AStarPath(path_points)

		self.algorithm_name = "FollowPath"
		self.set_algorithm(
			path=astar_path_instance,
			explicit_target=explicit_target,
			path_offset=1.0
		)
		
	def update_animation(self, dt):
		# Actualiza el temporizador de la animación
		self.animation_timer += dt
		
		# Si el temporizador supera la velocidad de la animación, cambia al siguiente fotograma
		if self.animation_timer >= self.animation_speed:
			self.animation_timer = 0.0 # Reinicia el temporizador
			# Obtiene la lista de fotogramas de la animación actual
			frames = self.animations[self.current_animation]
			# Avanza al siguiente fotograma, volviendo al inicio si llega al final
			self.current_frame_index = (self.current_frame_index + 1) % len(frames)
			# Actualiza el sprite actual al nuevo fotograma
			self.sprite = frames[self.current_frame_index]
			# Vuelve a generar la sombra para el nuevo sprite
			self.shadow_surface = self.sprite.copy()
			self.shadow_surface.fill((0, 0, 0, 100), special_flags=BLEND_RGBA_MULT)
		
	def set_algorithm(self, **params):
		# Configura el algoritmo de movimiento basado en el nombre y parámetros dados
		alg = SWITCHER_ALGORITHMS.get(self.algorithm_name, None)
		if not alg:
			return False
		self.algorithm_class = alg
		self.algorithm_params = params
		self.algorithm_instance = None
		return True
	
	def _ensure_algorithm_instance(self):
		# Asegura que la instancia del algoritmo esté creada
		if not self.algorithm_class:
			return None
		if self.algorithm_instance is None:
			# siempre inyectamos `character=self`; el resto vienen de algorithm_params
			kwargs = dict(self.algorithm_params)
			kwargs.setdefault("character", self)
			# el algoritmo puede definir sus propios parámetros (target, max_speed, ...)
			self.algorithm_instance = self.algorithm_class(**kwargs)
		return self.algorithm_instance

	def update_with_algorithm(self, dt, uses_rotation=False, bounds=None, margin=(0, 0), obstacles=None, nav_mesh=None):
		# Actualiza la posición y orientación del NPC usando el algoritmo de movimiento
		alg = self._ensure_algorithm_instance()
		if alg is None:
			return
		# obtener el steering del algoritmo y actualizar el kinematic
		steering = alg.get_steering()
		if hasattr(steering, 'linear') and hasattr(steering, 'angular'):
			# Si el steering es un SteeringOutput, acutualizar usando el método update
			if steering.linear.length() > 0 or steering.angular != 0:
				self.kinematic.update(steering, dt, self.rect, obstacles, 100, uses_rotation)
		elif hasattr(steering, 'velocity') and hasattr(steering, 'rotation'):
			# Si el steering es un KinematicSteeringOutput, actualizar directamente
			self.kinematic.position += steering.velocity * dt
			self.kinematic.orientation += steering.rotation * dt
		
		if nav_mesh:
			self.current_node_id = nav_mesh.find_node_at_position(self.kinematic.position, self.current_node_id)
		
		if bounds:
			# Determinar los límites mínimos y máximos para X e Y.
			min_x, min_y = 0, 0
			max_x, max_y = bounds[0], bounds[1]

			# Obtener el margen para el sprite.
			half_w, half_h = margin if margin and len(margin) == 2 else (0, 0)

			# Limitar la posición del personaje en el eje X.
			self.kinematic.position.x = max(min_x + half_w, min(self.kinematic.position.x, max_x - half_w))
			# Limitar la posición del personaje en el eje Y.
			self.kinematic.position.y = max(min_y + half_h, min(self.kinematic.position.y, max_y - half_h))