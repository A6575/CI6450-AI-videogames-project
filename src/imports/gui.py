# Configuración de la GUI con pygame
import pygame
from imports.character import Character
class GUI:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((800, 600))
		pygame.display.set_caption("Juego IA")
		self.clock = pygame.time.Clock()
	
	def display_character(self, character):
		# Nuevo tamaño (ancho, alto)
		nuevo_tamano = (30, 42)  # Por ejemplo, 30x52 píxeles

		# Escalar la imagen
		sprite_grande = pygame.transform.scale(character.sprite, nuevo_tamano)
		rotated_sprite = pygame.transform.rotate(sprite_grande, -character.kinematic.orientation)
		rect = rotated_sprite.get_rect(center=(character.kinematic.position.x, character.kinematic.position.y))
		self.screen.blit(rotated_sprite, rect)
	
	def update_character(self, character, linear, dt):
		keys = pygame.key.get_pressed()
		character.move(keys, linear, dt)
	
	def run(self):
		running = True
		player = Character("Hero", 100, self.screen.get_width() // 2, self.screen.get_height() // 2, is_player=True)
		dt = 0
		while running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False

			self.screen.fill((112, 112, 112))  # Fondo gris
			self.display_character(player)
			linear = pygame.math.Vector2(0, 0)
			self.update_character(player, linear, dt)
			pygame.display.flip()
			dt = self.clock.tick(60) / 1000
			
		pygame.quit()