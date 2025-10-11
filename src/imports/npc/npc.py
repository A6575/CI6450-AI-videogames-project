import math
from pygame.image import load
from pygame.math import Vector2
from pathlib import Path
from imports.moves.kinematic import Kinematic
from imports.moves.switcher import SWITCHER_ALGORITHMS

BASE_DIR = Path(__file__).resolve().parents[3]   # cuatro niveles arriba

class NPC:
	def __init__(self, name, health, x, y, algorithm_name=""):
		self.name = name
		self.health = health
		self.kinematic = Kinematic(
			position=Vector2(x, y),
			velocity=Vector2(0, 0), 
			orientation=270, 
			rotation=0
		)
		self.algorithm_name = algorithm_name
		self.map_width = 800   # valores por defecto; pueden cambiarse desde el exterior
		self.map_height = 600
		self.image = str(BASE_DIR / "assets" / "enemy.png")
		self.sprite = load(self.image).convert_alpha()

	def set_algorithm(self, **params):
		alg = SWITCHER_ALGORITHMS.get(self.algorithm_name, None)
		if not alg:
			self.algorithm_class = None
			self.algorithm_params = {}
			self.algorithm_instance = None
			return False
		self.algorithm_class = alg
		self.algorithm_params = params
		self.algorithm_instance = None
		return True
	
	def _ensure_algorithm_instance(self):
		if not self.algorithm_class:
			return None
		if self.algorithm_instance is None:
			# siempre inyectamos `character=self`; el resto vienen de algorithm_params
			kwargs = dict(self.algorithm_params)
			kwargs.setdefault("character", self)
			# el algoritmo puede definir sus propios parámetros (target, max_speed, ...)
			self.algorithm_instance = self.algorithm_class(**kwargs)
		return self.algorithm_instance

	def update_with_algorithm(self, dt):
		"""
		Actualiza la posición/orientación del NPC usando el algoritmo configurado.
		- Si el algoritmo define get_kinematic_steering(), se asume que devuelve una Vector2
			y/o que el algoritmo actualiza self.kinematic.velocity internamente.
		- Si define get_dynamic_steering(), se asume que devuelve un SteeringOutput y se
			aplica con Kinematic.update.
		"""
		alg = self._ensure_algorithm_instance()
		if alg is None:
			return

		steering = alg.get_steering()
		if hasattr(steering, 'linear') and hasattr(steering, 'angular'):
			# SteeringOutput
			self.kinematic.update(steering, dt, 100, False)
		elif hasattr(steering, 'velocity') and hasattr(steering, 'rotation'):
			self.kinematic.position += steering.velocity * dt
			self.kinematic.orientation += steering.rotation * dt
		
		# delimitar a dentro de la pantalla
		if self.kinematic.position.x < 0:
			self.kinematic.position.x = 0
		elif self.kinematic.position.x > self.map_width:
			self.kinematic.position.x = self.map_width

		if self.kinematic.position.y < 0:
			self.kinematic.position.y = 0
		elif self.kinematic.position.y > self.map_height:
			self.kinematic.position.y = self.map_height