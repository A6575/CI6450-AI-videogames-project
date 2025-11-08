from imports.moves.dynamic_arrive import DynamicArrive
from pygame.math import Vector2

class FollowPath:
	def __init__(self, character, path, explicit_target, path_offset=20.0):
		self.character = character				# El personaje que sigue el camino (NPC)
		self.explicit_target = explicit_target	# El objetivo explícito para la orientación (Player)
		self.path = path						# El camino a seguir (Path)
		self.path_offset = path_offset			# El offset del camino
		self.current_target_index = 0			# El índice del objetivo actual en el camino
		self.current_param = 0.0				# El parámetro actual en el camino
		self.arrive_behavior =  DynamicArrive(
			character=self.character, 
			target=self.explicit_target, 
			max_acceleration=150,
			max_speed=80,
			target_radius=2.0,
			slow_radius=15.0,
			time_to_target=0.1
		)

	def get_steering(self):
		# calcular el punto mas cercano en el path
		character_param = self.path.get_param(self.character.kinematic.position)
		target_param = character_param + self.path_offset
		target_position = self.path.get_position(target_param)

		# actualizar la posición del objetivo explícito
		self.explicit_target.kinematic.position = target_position
		
		return self.arrive_behavior.get_steering()
