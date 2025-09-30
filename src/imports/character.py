# Configuracion de los personajes (NPC y Player)
from imports.move import Kinematic
from pygame.math import Vector2

class Character:
	def __init__(self, name, health, x, y, is_player=False):
		self.name = name
		self.health = health
		self.is_player = is_player
		self.kinematic = Kinematic(
			position=Vector2(x, y),
			velocity=Vector2(0, 0), 
			orientation=270, 
			rotation=0
		)
