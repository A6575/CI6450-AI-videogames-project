import math
from pygame.image import load
from pygame.math import Vector2
from pathlib import Path
from imports.moves.kinematic import Kinematic

BASE_DIR = Path(__file__).resolve().parents[3]   # cuatro niveles arriba

class NPC:
	def __init__(self, name, health, x, y):
		self.name = name
		self.health = health
		self.kinematic = Kinematic(
			position=Vector2(x, y),
			velocity=Vector2(0, 0), 
			orientation=270, 
			rotation=0
		)
		
		self.image = str(BASE_DIR / "assets" / "npc.png")
		self.sprite = load(self.image).convert_alpha()