from imports.moves.dynamic_arrive import DynamicArrive
from pygame.math import Vector2

class FollowPath:
	def __init__(self, character, path, explicit_target, path_offset=20.0):
		self.character = character
		self.explicit_target = explicit_target
		self.path = path
		self.path_offset = path_offset
		self.current_target_index = 0

	def get_steering(self):
		# calcular el punto mas cercano en el path
		params = self.path.get_params(self.character.kinematic.position)
		closest_point = params["closest_point"]
		#print(closest_point)
		distance = params["distance"]
		# aplicar offset
		target_param = Vector2(closest_point.x + self.path_offset * params["path_direction"].x,
										closest_point.y + self.path_offset * params["path_direction"].y)
		self.explicit_target.kinematic.position = target_param
		arrive = DynamicArrive(
			character=self.character, 
			target=self.explicit_target, 
			max_acceleration=80,
			max_speed=80,
			target_radius=5.0,
			slow_radius=50.0,
			time_to_target=0.1
		)
		return arrive.get_steering()
