from imports.moves.align import Align
from imports.moves.kinematic import SteeringOutput
from pygame.math import Vector2
import math

class LookWhereYoureGoing:
	def __init__(self, character, explicit_target):
		self.character = character
		self.explicit_target = explicit_target

	def get_steering(self):
		if self.character.kinematic.velocity.length() == 0:
			return SteeringOutput(Vector2(0, 0), 0)  # No hay movimiento, no se necesita girar

		self.explicit_target.kinematic.orientation = math.degrees(math.atan2(-self.character.kinematic.velocity.x, -self.character.kinematic.velocity.y))

		align = Align(
			character=self.character,
			target=self.explicit_target,
			max_rotation=50,
			max_angular_acceleration=100,
			target_radius=5,
			slow_radius=10,
			time_to_target=0.1
		)

		result = align.get_steering()
		return result