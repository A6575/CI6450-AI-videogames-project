# Configuracion de los personajes (NPC y Player)
from imports.move import Kinematic, SteeringOutput
from pygame.math import Vector2
from pygame.image import load
from pygame import K_LEFT, K_RIGHT, K_UP, K_DOWN
from os import path

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

		if is_player:
			self.image = path.join(path.dirname(path.dirname(path.dirname(__file__))), "assets", "player.png")
			self.sprite = load(self.image).convert_alpha()

	def move(self, keys, linear, dt):
		if self.is_player:
			if keys[K_LEFT]:
				linear.x -= 1
			if keys[K_RIGHT]:
				linear.x += 1
			if keys[K_UP]:
				linear.y -= 1
			if keys[K_DOWN]:
				linear.y += 1
			if linear.length() > 0:
				linear = linear.normalize() * 100 
			steering = SteeringOutput(linear, 0)
			self.kinematic.update(steering, dt)