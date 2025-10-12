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
		uses_rotation = scenario_type in ["Align", "VelocityMatch", "Face", "DynamicWander", "BlendedSteeringLWYG"]
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
			case "Evade":
				enemy.set_algorithm(evade_target=target, max_prediction=0.5, explicit_target=Player("Target", 0, 0, 0))
			case "Face":
				enemy.set_algorithm(face_target=target, explicit_target=Player("Target", 0, 0, 0))
			case "BlendedSteeringLWYG":
				# Comportamientos a combinar
				movement_behavior = {
					"Pursue": {"max_prediction": 0.5, "pursue_target": target},
					# "Evade": {"max_prediction": 0.5, "evade_target": target}  # Descomentar para probar Evade en lugar de Pursue
				}
				enemy.set_algorithm(movement_behavior=movement_behavior, explicit_target=Player("Target", 0, 0, 0))
		return enemy, uses_rotation
	
	def run(self):
		running = True
		player = Player(
			"Hero", 
			100, 
			self.screen.get_width() // 2,
			self.screen.get_height() // 2,
		)
		enemy, uses_rotation = self.set_enemy_algorithm("BlendedSteeringLWYG", target=player)
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