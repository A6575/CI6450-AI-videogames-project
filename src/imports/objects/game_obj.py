import pygame
import math
import time
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
	def __init__(self, x, y, node_id, has_pot=False):
		super().__init__(x, y, str(BASE_DIR / "assets" / "webs" / "spiderweb_4.png"), node_id, size=(100, 100))
		self.float_range = 0
		self.has_pot = has_pot
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

class SpiderProjectile(pygame.sprite.Sprite):
	def __init__(self,
			  x,
			  y,
			  direction_vector,
			  owner=None,
			  speed = 200,
			  damage = 40,
			  lifetime = 3000,
			  stick_duration = 2000,
			  blink_duration = 200):
		super().__init__()
		self.owner = owner
		self.world = None
		self.frames = []
		self.frame_index = 0
		self.frame_interval = 80
		self.last_frame_update = pygame.time.get_ticks()
		
		originals_image = [
			pygame.image.load(str(BASE_DIR/ "assets" / "attack" / "enemy" / "1-spider-web.png")),
			pygame.image.load(str(BASE_DIR/ "assets" / "attack" / "enemy" / "2-spider-web.png")),
			pygame.image.load(str(BASE_DIR/ "assets" / "attack" / "enemy" / "3-spider-web.png")),
			pygame.image.load(str(BASE_DIR/ "assets" / "attack" / "enemy" / "4-spider-web.png")),
			pygame.image.load(str(BASE_DIR/ "assets" / "attack" / "enemy" / "5-spider-web.png")),
		]
		for img in originals_image:
			self.frames.append(img.convert_alpha())
		
		self.base_image = self.frames[0]
		self.base_size = self.base_image.get_size()
		self.image = pygame.transform.scale(self.frames[self.frame_index], (40, 40))
		self.rect = self.image.get_rect(center=(x, y))

		self.speed = speed
		self.velocity = direction_vector * self.speed
		self.lifetime = lifetime
		self.spawn_time = pygame.time.get_ticks()
		self.damage = damage
		self.attached = False
		self.attached_to = None
		self.stick_started_at = None
		self.stick_duration = stick_duration
		self.blink_duration = blink_duration
		self._applied_damage = False

	def update(self, dt):
		now = pygame.time.get_ticks()

		if self.attached and self.attached_to:
			px, py = self._get_entity_center(self.attached_to)
			self.rect.center = (px, py)
			if self.stick_started_at and now - self.stick_started_at >= self.stick_duration:
				self.kill()
			self._advance_animation(now)
			return
		self.rect.x += self.velocity.x * dt
		self.rect.y += self.velocity.y * dt
		self._advance_animation(now)
		if now - self.spawn_time > self.lifetime:
			self.kill()

		if self.world and hasattr(self.world, 'player') and self.world.player:
			if self.rect.colliderect(self.world.player.rect):
				self._on_hit_player(self.world.player)
	
	def _advance_animation(self, now):
		if not self.frames:
			return
		if now - self.last_frame_update >= self.frame_interval:
			self.frame_index = (self.frame_index + 1) % len(self.frames)
			self.image = pygame.transform.scale(self.frames[self.frame_index], (40, 40))
			self.last_frame_update = now
	
	def _on_hit_player(self, player):
		if self.attached:
			return
		self.attached = True
		self.attached_to = player
		self.stick_started_at = pygame.time.get_ticks()

		try:
			if hasattr(player, 'take_damage') and callable(player.take_damage):
				player.take_damage(self.damage)
			else:
				#setattr(player, 'is_hit', True)
				setattr(player, 'health', getattr(player, 'health', 100) - self.damage)
		except Exception as e:
			print(f"Error applying damage to player: {e}")

		blink_secs = float(self.blink_duration)
		setattr(player, '_blink_until', time.time() + blink_secs)
		self.rect.center = (player.rect.centerx, player.rect.top - 12)
		if self.owner and hasattr(self.owner, 'emit_hsm_event'):
			self.owner.emit_hsm_event('jugador_cae_en_red')

	def _get_entity_center(self, entity):
		if hasattr(entity, 'rect'):
			return entity.rect.center
		if hasattr(entity, 'kinematic') and hasattr(entity.kinematic, 'position'):
			pos = entity.kinematic.position
			return (pos.x, pos.y)
		return self.rect.center