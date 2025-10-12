from imports.moves.align import Align
from imports.moves.kinematic import SteeringOutput
import math

class Face:
	def __init__(self, character, face_target, explicit_target) -> None:
		self.character = character
		self.face_target = face_target
		self.explicit_target = explicit_target

	def get_steering(self):
		direction = self.face_target.kinematic.position - self.character.kinematic.position
		
		if direction.length() == 0:
			return SteeringOutput(linear=direction, angular=0)
		
		self.explicit_target.kinematic.orientation = math.degrees(math.atan2(-direction.x, -direction.y))

		align = Align(
			character=self.character,
			target=self.explicit_target,
			max_rotation=50,
			max_angular_acceleration=100,
			target_radius=5,
			slow_radius=10,
			time_to_target=0.1
		)

		return align.get_steering()
