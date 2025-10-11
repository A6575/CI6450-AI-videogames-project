# Configuración de la GUI con pygame
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
	
	def run(self):
		running = True
		player = Player(
			"Hero", 
			100, 
			self.screen.get_width() // 2,
			self.screen.get_height() // 2,
		)
		enemy = NPC(
			"Dynamic Flee",
			100,
			self.screen.get_width()//2,
			self.screen.get_height()//2,
			"DynamicFlee"
		)
		enemy.set_algorithm(target=player, max_acceleration=80)
		dt = 0
		while running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False

			self.screen.fill((112, 112, 112))
			self.display_character(player)
			self.display_character(enemy)
			enemy.update_with_algorithm(dt)
			linear = pygame.math.Vector2(0, 0)
			bounds = (self.screen.get_width(), self.screen.get_height())
			margin = (self.sprite_size[0] / 2, self.sprite_size[1] / 2)
			self.update_character(player, linear, dt, bounds=bounds, margin=margin)
			pygame.display.flip()
			dt = self.clock.tick(60) / 1000
			
		pygame.quit()