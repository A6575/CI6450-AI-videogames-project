# Configuracion de los personajes (NPC y Player)
from imports.moves.kinematic import Kinematic, SteeringOutput
from pygame import BLEND_RGBA_MULT
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
		
		# Rutas a las imágenes de la animación del personaje
		self.animation_images = [
			str(BASE_DIR / "assets" / "player" / "bee-1.png"),
			str(BASE_DIR / "assets" / "player" / "bee-2.png"),
			str(BASE_DIR / "assets" / "player" / "bee-3.png"),
			str(BASE_DIR / "assets" / "player" / "bee-4.png")
		]
		# Cargar las superficies de Pygame para cada imagen
		self.animation_frames = [load(img).convert_alpha() for img in self.animation_images]
		self.current_frame_index = 0 # Índice del fotograma actual
		self.sprite = self.animation_frames[self.current_frame_index] # Sprite actual
		self.sprite_size = (35, 35)						 	 # Tamaño del sprite del personaje
		self.rect = self.sprite.get_rect(center=(x, y))

		# --- Variables para el control de la animación ---
		self.animation_timer = 0.0 # Temporizador para cambiar de fotograma
		self.animation_speed = 0.1 # Tiempo en segundos que dura cada fotograma

		# Crear una superficie para la sombra del mismo tamaño que el sprite original
		self.shadow_surface = self.sprite.copy()
		# Rellenar la superficie de la sombra con un color negro semi-transparente
		self.shadow_surface.fill((0, 0, 0, 100), special_flags=BLEND_RGBA_MULT)
	
	def update_animation(self, dt):
		# Actualiza el temporizador de la animación
		self.animation_timer += dt
		
		# Si el temporizador supera la velocidad de la animación, cambia al siguiente fotograma
		if self.animation_timer >= self.animation_speed:
			self.animation_timer = 0.0 # Reinicia el temporizador
			# Avanza al siguiente fotograma, volviendo al inicio si llega al final
			self.current_frame_index = (self.current_frame_index + 1) % len(self.animation_frames)
			# Actualiza el sprite actual al nuevo fotograma
			self.sprite = self.animation_frames[self.current_frame_index]
			# Vuelve a generar la sombra para el nuevo sprite
			self.shadow_surface = self.sprite.copy()
			self.shadow_surface.fill((0, 0, 0, 100), special_flags=BLEND_RGBA_MULT)
			
	# Mover el personaje basado en la entrada del teclado
	def move(self, keys, linear, dt, bounds=None, margin=(0, 0), obstacles=None):
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

		self.kinematic.update(steering, dt, self.rect, obstacles, 120)

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