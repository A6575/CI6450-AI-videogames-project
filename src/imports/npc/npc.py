import math
from pygame.image import load
from pygame.math import Vector2
from pathlib import Path
from imports.moves.kinematic import Kinematic
from imports.moves.switcher import SWITCHER_ALGORITHMS

# Directorio base para cargar recursos
BASE_DIR = Path(__file__).resolve().parents[3]   # cuatro niveles arriba

class NPC:
	def __init__(self, name, health, x, y, algorithm_name=""):
		self.name = name				# Nombre del NPC
		self.health = health			# Salud del NPC
		self.kinematic = Kinematic(		# Estado cinemático del NPC
			position=Vector2(x, y),
			velocity=Vector2(0, 0), 
			orientation=270, 
			rotation=0
		)
		self.algorithm_name = algorithm_name	# Nombre del algoritmo de movimiento
		self.map_width = 800   # valores por defecto de tamaño del mapa
		self.map_height = 600
		self.image = str(BASE_DIR / "assets" / "enemy.png") # Ruta a la imagen del NPC
		self.sprite = load(self.image).convert_alpha()		# Cargar la imagen del NPC

	def set_algorithm(self, **params):
		# Configura el algoritmo de movimiento basado en el nombre y parámetros dados
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
		# Asegura que la instancia del algoritmo esté creada
		if not self.algorithm_class:
			return None
		if self.algorithm_instance is None:
			# siempre inyectamos `character=self`; el resto vienen de algorithm_params
			kwargs = dict(self.algorithm_params)
			kwargs.setdefault("character", self)
			# el algoritmo puede definir sus propios parámetros (target, max_speed, ...)
			self.algorithm_instance = self.algorithm_class(**kwargs)
		return self.algorithm_instance

	def update_with_algorithm(self, dt, uses_rotation=False, teletransport=False):
		# Actualiza la posición y orientación del NPC usando el algoritmo de movimiento
		alg = self._ensure_algorithm_instance()
		if alg is None:
			return
		# obtener el steering del algoritmo y actualizar el kinematic
		steering = alg.get_steering()
		if hasattr(steering, 'linear') and hasattr(steering, 'angular'):
			# Si el steering es un SteeringOutput, acutualizar usando el método update
			if steering.linear.length() > 0 or steering.angular != 0:
				self.kinematic.update(steering, dt, 100, uses_rotation)
		elif hasattr(steering, 'velocity') and hasattr(steering, 'rotation'):
			# Si el steering es un KinematicSteeringOutput, actualizar directamente
			self.kinematic.position += steering.velocity * dt
			self.kinematic.orientation += steering.rotation * dt
		
		if teletransport:
			# Teletransportar al NPC si sale de los límites del mapa
			if self.kinematic.position.x < -10:
				self.kinematic.position.x = self.map_width
			elif self.kinematic.position.x > self.map_width + 10:
				self.kinematic.position.x = 0
			if self.kinematic.position.y < -10:
				self.kinematic.position.y = self.map_height
			elif self.kinematic.position.y > self.map_height + 10:
				self.kinematic.position.y = 0
		else:
			# delimitar a dentro de la pantalla
			if self.kinematic.position.x < 0:
				self.kinematic.position.x = 0
			elif self.kinematic.position.x > self.map_width:
				self.kinematic.position.x = self.map_width

			if self.kinematic.position.y < 0:
				self.kinematic.position.y = 0
			elif self.kinematic.position.y > self.map_height:
				self.kinematic.position.y = self.map_height