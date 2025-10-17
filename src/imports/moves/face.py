from imports.moves.align import Align
from imports.moves.kinematic import SteeringOutput
import math

class Face:
	def __init__(self, character, face_target, explicit_target):
		self.character = character				# El personaje que realiza la acción de mirar (NPC)
		self.face_target = face_target			# El objetivo al que se está mirando (Player)
		self.explicit_target = explicit_target	# El objetivo explícito para la acción de mirar (Align)

	def get_steering(self):
		# Vector desde el personaje al objetivo
		direction = self.face_target.kinematic.position - self.character.kinematic.position
		
		# Si la dirección es cero, no se necesita rotación
		if direction.length() == 0:
			return SteeringOutput(linear=direction, angular=0)
		
		# Orientación del personaje hacia el objetivo
		self.explicit_target.kinematic.orientation = math.degrees(math.atan2(-direction.x, -direction.y))

		# Usar Align para alinear la orientación del personaje con la del objetivo
		align = Align(
			character=self.character,
			target=self.explicit_target,
			max_rotation=100,
			max_angular_acceleration=150,
			target_radius=5,
			slow_radius=10,
			time_to_target=0.1
		)

		return align.get_steering()
