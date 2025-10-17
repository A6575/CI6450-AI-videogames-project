# Configuracion de los personajes (NPC y Player)
from imports.moves.kinematic import Kinematic, SteeringOutput
from pygame.math import Vector2
from pygame.image import load
from pygame import K_LEFT, K_RIGHT, K_UP, K_DOWN
from pathlib import Path

# Definir la ruta base para cargar imágenes
BASE_DIR = Path(__file__).resolve().parents[3]   # cuatro niveles arriba

class Player:
	def __init__(self, name, health, x, y):
		self.name = name				# Nombre del personaje
		self.health = health			# Salud del personaje
		self.kinematic = Kinematic(		# Estado cinemático del personaje
			position=Vector2(x, y),
			velocity=Vector2(0, 0), 
			orientation=270, 
			rotation=0
		)
		
		self.image = str(BASE_DIR / "assets" / "player.png") # Ruta a la imagen del personaje
		self.sprite = load(self.image).convert_alpha()		 # Cargar la imagen del personaje

	# Mover el personaje basado en la entrada del teclado
	def move(self, keys, linear, dt, bounds=None, margin=(0, 0)):
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
		
		# Crear un SteeringOutput con la velocidad calculada 
		steering = SteeringOutput(linear, 0)
		
		self.kinematic.update(steering, dt, 120)

		# Limitar movimiento a los bordes de la pantalla
		if bounds:
			# Determinar min y max de x e y
			if len(bounds) == 2:
				min_x, min_y = 0, 0
				max_x, max_y = bounds[0], bounds[1]
			else:
				print("Error: bounds debe ser una tupla de 2 elementos.")
				return

			half_w, half_h = margin if margin and len(margin) == 2 else (0, 0)
			# Asegurar que min es menor que max
			if max_x < min_x:
				min_x, max_x = max_x, min_x
			if max_y < min_y:
				min_y, max_y = max_y, min_y

			# Limitar posición del personaje
			self.kinematic.position.x = max(min_x + half_w, min(self.kinematic.position.x, max_x - half_w))
			self.kinematic.position.y = max(min_y + half_h, min(self.kinematic.position.y, max_y - half_h))