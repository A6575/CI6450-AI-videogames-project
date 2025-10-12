# Configuración de la GUI con pygame
import math
import pygame
from imports.player.player import Player
from imports.npc.npc import NPC
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

		pos = (int(character.kinematic.position.x), int(character.kinematic.position.y))
		radius = 25
		pygame.draw.circle(self.screen, (0, 200, 255), pos, radius, 2)

		# Calcular punto final de la flecha según orientación
		angle_rad = -character.kinematic.orientation * (3.14159265 / 180)
		end_x = pos[0] + int(radius * 0.8 * math.cos(angle_rad))
		end_y = pos[1] + int(radius * 0.8 * math.sin(angle_rad))
		end_pos = (end_x, end_y)
		pygame.draw.line(self.screen, (255, 50, 50), pos, end_pos, 3)

		# Dibujar cabeza de flecha
		arrow_size = 8
		arrow_angle = 0.5  # radianes
		left_x = end_x + int(arrow_size * math.cos(angle_rad + arrow_angle))
		left_y = end_y + int(arrow_size * math.sin(angle_rad + arrow_angle))
		right_x = end_x + int(arrow_size * math.cos(angle_rad - arrow_angle))
		right_y = end_y + int(arrow_size * math.sin(angle_rad - arrow_angle))
		pygame.draw.line(self.screen, (255, 50, 50), end_pos, (left_x, left_y), 2)
		pygame.draw.line(self.screen, (255, 50, 50), end_pos, (right_x, right_y), 2)
	
	def update_character(self, character, linear, dt, bounds=None, margin=(0, 0)):
		keys = pygame.key.get_pressed()
		character.move(keys, linear, dt, bounds=bounds, margin=margin)
	
	def set_enemy_algorithm(self, scenario_type, target):
		enemy = NPC(
					scenario_type,
					100,
					self.screen.get_width()//4,
					self.screen.get_height()//4,
					scenario_type
				)
		uses_rotation = scenario_type in ["Align"]
		match scenario_type:
			case "KinematicSeek":
				enemy.set_algorithm(target=target, max_speed=80)
			case "KinematicArrive":
				enemy.set_algorithm(target=target, max_speed=80, target_radius=5.0, time_to_target=0.1)
			case "KinematicFlee":
				enemy.set_algorithm(target=target, max_speed=20)
			case "KinematicWander":
				enemy.set_algorithm(max_speed=20, max_rotation=150)
			case "DynamicSeek":
				enemy.set_algorithm(target=target, max_acceleration=80)
			case "DynamicArrive":
				enemy.set_algorithm(target=target, max_acceleration=80, max_speed=80, target_radius=5.0, slow_radius=50.0, time_to_target=0.1)
			case "DynamicFlee":
				enemy.set_algorithm(target=target, max_acceleration=10)
			case "Align":
				enemy.set_algorithm(target=target, max_rotation=50, max_angular_acceleration=100, target_radius=5, slow_radius=10, time_to_target=0.1)
			case "VelocityMatch":
				enemy.set_algorithm(target=target, max_acceleration=50, time_to_target=0.1)
			case "Pursue":
				enemy.set_algorithm(pursue_target=target, max_prediction=0.5, explicit_target=Player("Target", 0, 0, 0))
		return enemy, uses_rotation
	
	def run(self):
		running = True
		player = Player(
			"Hero", 
			100, 
			self.screen.get_width() // 2,
			self.screen.get_height() // 2,
		)
		enemy, uses_rotation = self.set_enemy_algorithm("Pursue", target=player)
		dt = 0
		while running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False

			self.screen.fill((112, 112, 112))
			self.display_character(player)
			self.display_character(enemy)
			enemy.update_with_algorithm(dt, uses_rotation=uses_rotation)
			linear = pygame.math.Vector2(0, 0)
			bounds = (self.screen.get_width(), self.screen.get_height())
			margin = (self.sprite_size[0] / 2, self.sprite_size[1] / 2)
			self.update_character(player, linear, dt, bounds=bounds, margin=margin)
			pygame.display.flip()
			dt = self.clock.tick(60) / 1000
			
		pygame.quit()