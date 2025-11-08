import pygame
import math
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]   # cuatro niveles arriba

class GameObject(pygame.sprite.Sprite):
	def __init__(self, x, y, image_path, node_id, size=(20, 20)):
		super().__init__()
		original_image = pygame.image.load(image_path).convert_alpha()
		self.image = pygame.transform.scale(original_image, size)
		self.shadow_surface = self.image.copy()
		self.shadow_surface.fill((0, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
		self.initial_pos = (x, y)
		self.rect = self.image.get_rect(center=self.initial_pos)
		self.node_id = node_id
		self.animation_timer = 0.0
		self.float_speed = 1.5
		self.float_range = 4

	def update(self, dt):
		self.animation_timer += dt * self.float_speed
		offset = math.sin(self.animation_timer) * self.float_range
		self.rect.centery = self.initial_pos[1] + offset

class HoneyPot(GameObject):
	def __init__(self, x, y, node_id, on_web=False):
		super().__init__(x, y, str(BASE_DIR / "assets" / "objects" / "2-honeyjar-v2.png"), node_id)
		self.on_web = on_web

class PowerUp(GameObject):
	def __init__(self, x, y, node_id):
		super().__init__(x, y, str(BASE_DIR / "assets" / "objects" / "power-up-1.png"), node_id)
		self.duration = 10000

class SpiderWeb(GameObject):
	def __init__(self, x, y, node_id):
		super().__init__(x, y, str(BASE_DIR / "assets" / "webs" / "spiderweb_4.png"), node_id, size=(100, 100))
		self.float_range = 0

class SeedProjectile(pygame.sprite.Sprite):
	def __init__(self, x, y, direction_vector):
		super().__init__()

		original_image = pygame.image.load(str(BASE_DIR / "assets" / "attack" / "player" / "1-seed.png")).convert_alpha()
		self.image = pygame.transform.scale(original_image, (15, 15))
		self.rect = self.image.get_rect(center=(x, y))

		self.velocity = direction_vector * 300
		self.lifetime = 2000
		self.spawn_time = pygame.time.get_ticks()
		self.damage = 40

	def update(self, dt):
		self.rect.x += self.velocity.x * dt
		self.rect.y += self.velocity.y * dt

		if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
			self.kill()