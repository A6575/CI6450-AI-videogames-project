# Configuración de la GUI con pygame
import pygame
from imports.character import Character
from imports.move import SteeringOutput
class GUI:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((800, 600))
		pygame.display.set_caption("Juego IA")
		self.clock = pygame.time.Clock()
	
	def draw_character(self, character):
		# Definir color según el tipo de personaje
		if character.is_player:
			color = (0, 255, 0)  # Verde para el jugador
		else:
			color = (255, 0, 0)  # Rojo para NPCs

		# Posición y tamaño del triángulo
		x, y = character.kinematic.position.x, character.kinematic.position.y
		size = 25
		points = [
			(x, y - size // 2),  # Punta superior
			(x - size // 2, y + size // 2),  # Esquina inferior izquierda
			(x + size // 2, y + size // 2)   # Esquina inferior derecha
		]
		pygame.draw.polygon(self.screen, color, points)

		# Mostrar nombre y salud
		""" font = pygame.font.Font(None, 36)
		text = font.render(f"{character.name}: {character.health} HP", True, (255, 255, 255))
		self.screen.blit(text, (10, 10)) """
	def update_character(self, character, dt):
		keys = pygame.key.get_pressed()
		linear = pygame.math.Vector2(0, 0)
		if character.is_player:
			if keys[pygame.K_LEFT]:
				linear.x -= 1
			if keys[pygame.K_RIGHT]:
				linear.x += 1
			if keys[pygame.K_UP]:
				linear.y -= 1
			if keys[pygame.K_DOWN]:
				linear.y += 1
			if linear.length() > 0:
				linear = linear.normalize() * 100  # velocidad es un valor como 100
			steering = SteeringOutput(linear, 0)
			character.kinematic.update(steering, dt)
	def run(self):
		running = True
		player = Character("Hero", 100, self.screen.get_width() // 2, self.screen.get_height() // 2, is_player=True)
		dt = 0
		while running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False

			self.screen.fill('darkslategray')
			self.draw_character(player)
			self.update_character(player, dt)
			pygame.display.flip()
			dt = self.clock.tick(60) / 1000 
		pygame.quit()