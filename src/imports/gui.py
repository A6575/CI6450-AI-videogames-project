# Configuración de la GUI con pygame
import random
import math
import pygame
from imports.player.player import Player
from imports.npc.npc import NPC
from imports.map.path import Path
class GUI:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((800, 600))
		pygame.display.set_caption("Juego IA")
		self.clock = pygame.time.Clock()
		# Tamaño del sprite usado para dibujar y para calcular márgenes
		self.sprite_size = (30, 42)
	
	def display_character(self, character):
		# Escalar png y rotar segun orientacion
		sprite_grande = pygame.transform.scale(character.sprite, self.sprite_size)
		rotated_sprite = pygame.transform.rotate(sprite_grande, character.kinematic.orientation)
		rect = rotated_sprite.get_rect(center=(character.kinematic.position.x, character.kinematic.position.y))
		self.screen.blit(rotated_sprite, rect)

		# Fuente para mostrar nombres
		self.font = pygame.font.SysFont(None, 16)

		# Mostrar nombre arriba del personaje
		name_surface = self.font.render(character.name, True, (255, 255, 255))
		name_rect = name_surface.get_rect(center=(character.kinematic.position.x, character.kinematic.position.y - self.sprite_size[1] // 2 - 10))
		self.screen.blit(name_surface, name_rect)
	def display_path(self, path):
		points = path.get_path()
		if len(points) < 2:
			return
		# Dibujar líneas entre los puntos del camino
		for i in range(len(points) - 1):
			start_pos = (points[i].x, points[i].y)
			end_pos = (points[i + 1].x, points[i + 1].y)
			if i % 2 == 0:
				pygame.draw.line(self.screen, (0, 0, 0), start_pos, end_pos, 2)
			else:
				pygame.draw.line(self.screen, (255, 255, 0), start_pos, end_pos, 2)

	def update_character(self, character, linear, dt, bounds=None, margin=(0, 0)):
		keys = pygame.key.get_pressed()
		character.move(keys, linear, dt, bounds=bounds, margin=margin)
	
	def set_enemy_algorithm(self, scenario_type, target, path):
		enemies = []
		uses_rotation = scenario_type in ["Align", "VelocityMatch", "Face", "DynamicWander", "BlendedSteeringLWYG", "ObstacleAvoidance"]
		match scenario_type:
			case "KinematicSeek":
				enemies.append(NPC(
					scenario_type,
					100,
					self.screen.get_width()//4,
					self.screen.get_height()//4,
					scenario_type
				))
				enemies[0].set_algorithm(target=target, max_speed=80)
			case "KinematicArrive":
				enemies.append(NPC(
					scenario_type,
					100,
					self.screen.get_width()//4,
					self.screen.get_height()//4,
					scenario_type
				))
				enemies[0].set_algorithm(target=target, max_speed=80, target_radius=5.0, time_to_target=0.1)
			case "KinematicFlee":
				enemies.append(NPC(
					scenario_type,
					100,
					self.screen.get_width()//4,
					self.screen.get_height()//4,
					scenario_type
				))
				enemies[0].set_algorithm(target=target, max_speed=20)
			case "KinematicWander":
				for _ in range(5):
					enemies.append(NPC(
						scenario_type,
						100,
						random.randint(0, self.screen.get_width()),
						random.randint(0, self.screen.get_height()),
						scenario_type
					))
					enemies[-1].kinematic.orientation = random.randint(0, 360)
					enemies[-1].set_algorithm(max_speed=20, max_rotation=150)
			case "DynamicSeek":
				enemies.append(NPC(
					scenario_type,
					100,
					self.screen.get_width()//4,
					self.screen.get_height()//4,
					scenario_type
				))
				enemies[0].set_algorithm(target=target, max_acceleration=80)
			case "DynamicArrive":
				enemies.append(NPC(
					scenario_type,
					100,
					self.screen.get_width()//4,
					self.screen.get_height()//4,
					scenario_type
				))
				enemies[0].set_algorithm(target=target, max_acceleration=80, max_speed=80, target_radius=5.0, slow_radius=50.0, time_to_target=0.1)
			case "DynamicFlee":
				enemies.append(NPC(
					scenario_type,
					100,
					self.screen.get_width()//4,
					self.screen.get_height()//4,
					scenario_type
				))
				enemies[0].set_algorithm(target=target, max_acceleration=10)
			case "Align":
				enemies.append(NPC(
					scenario_type,
					100,
					self.screen.get_width()//4,
					self.screen.get_height()//4,
					scenario_type
				))
				enemies[0].set_algorithm(target=target, max_rotation=50, max_angular_acceleration=100, target_radius=5, slow_radius=10, time_to_target=0.1)
			case "VelocityMatch":
				enemies.append(NPC(
					scenario_type,
					100,
					self.screen.get_width()//4,
					self.screen.get_height()//4,
					scenario_type
				))
				enemies[0].set_algorithm(target=target, max_acceleration=50, time_to_target=0.1)
			case "Pursue":
				enemies.append(NPC(
					scenario_type,
					100,
					self.screen.get_width()//4,
					self.screen.get_height()//4,
					scenario_type
				))
				enemies[0].set_algorithm(pursue_target=target, max_prediction=0.5, explicit_target=Player("Target", 0, 0, 0))
			case "Evade":
				enemies.append(NPC(
					scenario_type,
					100,
					self.screen.get_width()//4,
					self.screen.get_height()//4,
					scenario_type
				))
				enemies[0].set_algorithm(evade_target=target, max_prediction=0.5, explicit_target=Player("Target", 0, 0, 0))
			case "Face":
				num_npcs = 10
				radius = 150
				player_pos = target.kinematic.position

				for i in range(num_npcs):
					angle = (2 * math.pi / num_npcs) * i
					
					enemies.append(NPC(
						f"Face-{i+1}",
						100,
						player_pos.x + radius * math.cos(angle),
						player_pos.y + radius * math.sin(angle),
						scenario_type
					))
					enemies[-1].kinematic.orientation = random.randint(0, 360)
					enemies[-1].set_algorithm(face_target=target, explicit_target=Player("Target", 0, 0, 0))
			case "BlendedSteeringLWYG":
				enemies.append(NPC(
					"LWYG+Pursue",
					100,
					self.screen.get_width()//4,
					self.screen.get_height()//4,
					scenario_type
				))
				# Comportamientos a combinar
				pursue_movement_behavior = {
					"Pursue": {"max_prediction": 0.5, "pursue_target": target},
				}
				enemies[-1].set_algorithm(movement_behavior=pursue_movement_behavior, explicit_target=Player("Target", 0, 0, 0))

				enemies.append(NPC(
					"LWYG+Evade",
					100,
					self.screen.get_width()//2,
					self.screen.get_height()//2,
					scenario_type
				))
				# Comportamientos a combinar
				evade_movement_behavior = {
					"Evade": {"max_prediction": 0.5, "evade_target": target}
				}
				enemies[-1].set_algorithm(movement_behavior=evade_movement_behavior, explicit_target=Player("Target", 0, 0, 0))
			case "FollowPath":
				path_points = path.get_path()

				min_x = min(point.x for point in path_points)
				max_x = max(point.x for point in path_points)
				min_y = min(point.y for point in path_points)
				max_y = max(point.y for point in path_points)

				path_box = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

				num_npc_inside = 2
				num_npc_outside = 3
				for i in range(num_npc_inside):
					enemies.append(NPC(
						f"Inside-{i+1}",
						100,
						random.uniform(path_box.left, path_box.right),
						random.uniform(path_box.top, path_box.bottom),
						scenario_type
					))
					enemies[-1].kinematic.orientation = random.randint(0, 360)
					enemies[-1].set_algorithm(path=path, explicit_target=Player("Target", 0, 0, 0))
				
				for i in range(num_npc_outside):
					pos_x, pos_y = 0, 0
					# Repetir hasta encontrar un punto que esté fuera del bounding box
					while True:
						pos_x = random.randint(0, self.screen.get_width())
						pos_y = random.randint(0, self.screen.get_height())
						# collidepoint comprueba si un punto está dentro de un Rect
						if not path_box.collidepoint(pos_x, pos_y):
							break
					
					enemies.append(NPC(
						f"Outside-{i+1}",
						100,
						pos_x,
						pos_y,
						scenario_type
					))
					enemies[-1].kinematic.orientation = random.randint(0, 360)
					enemies[-1].set_algorithm(path=path, explicit_target=Player("Target", 0, 0, 0))
			case "DynamicWander":
				for _ in range(5):
					enemies.append(NPC(
						scenario_type,
						100,
						random.randint(0, self.screen.get_width()),
						random.randint(0, self.screen.get_height()),
						scenario_type
					))
					enemies[-1].kinematic.orientation = random.randint(0, 360)
					enemies[-1].set_algorithm(max_acceleration=50, wander_target=Player("WanderTarget", 0, 0, 0), explicit_target=Player("Target", 0, 0, 0))
			case "PrioritySteering":
				for i in range(5):
					npc = NPC(f"Blue-{i}", 100, 150 + i * 40, 150, scenario_type)
					npc.kinematic.orientation = 135 # Mirando hacia el grupo rojo
					enemies.append(npc)
				for i in range(5):
					npc = NPC(f"Red-{i}", 100, 550 - i * 40, 450, "PrioritySteering")
					npc.kinematic.orientation = -45 # Mirando hacia el grupo azul
					enemies.append(npc)
				behavior = {
					"CollisionAvoidance": {"all_characters": enemies, "radius": 30, "max_acceleration": 5},
					"DynamicWander": {"max_acceleration": 10, "wander_target": Player("WanderTarget", 0, 0, 0), "explicit_target": Player("Target", 0, 0, 0)}
				}
				for enemy in enemies:
					enemy.set_algorithm(behaviors=behavior)
		return enemies, uses_rotation

	def run(self, draw_path, scenario_type):
		running = True
		player = Player(
			"Hero", 
			100, 
			self.screen.get_width() // 2,
			self.screen.get_height() // 2,
		)
		path = Path(pygame.Vector2(400,150))
		enemies, uses_rotation = self.set_enemy_algorithm(scenario_type, target=player, path=path)
		dt = 0
		while running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False

			self.screen.fill((112, 112, 112))
			if draw_path:
				self.display_path(path)
		
			self.display_character(player)
			for enemy in enemies:
				self.display_character(enemy)
				enemy.update_with_algorithm(dt, uses_rotation=uses_rotation)
			linear = pygame.math.Vector2(0, 0)
			bounds = (self.screen.get_width(), self.screen.get_height())
			margin = (self.sprite_size[0] / 2, self.sprite_size[1] / 2)
			self.update_character(player, linear, dt, bounds=bounds, margin=margin)
			pygame.display.flip()
			dt = self.clock.tick(60) / 1000
			
		pygame.quit()