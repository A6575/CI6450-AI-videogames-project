import random
from imports.moves.face import Face

class DynamicWander:
	def __init__(self, character, max_acceleration, wander_target, explicit_target, wander_offset=8.0, wander_radius=10.0, wander_rate=0.9):
		self.character = character					# El personaje que se va a mover (NPC)
		self.max_acceleration = max_acceleration	# La aceleración máxima del personaje
		self.wander_target = wander_target			# El objetivo al cual se va a mover (target de wander)
		self.explicit_target = explicit_target		# El objetivo explícito para Face
		self.wander_offset = wander_offset			# El offset de wander para posicionar el círculo delante del personaje
		self.wander_radius = wander_radius			# El radio del círculo de wander
		self.wander_rate = wander_rate				# La tasa de cambio de la orientación del wander
		self.wander_orientation = 0.0				# La orientación inicial del wander

	def _random_binomial(self):
		# Devuelve un valor aleatorio en el rango [-1, 1]
		return random.random() - random.random()
	
	def get_steering(self):
		# Actualizar la orientación del wander
		self.wander_orientation += self._random_binomial() * self.wander_rate # type: ignore

		# Calcular la posición del target de wander
		self.wander_target.kinematic.orientation = self.wander_orientation + self.character.kinematic.orientation
		self.wander_target.kinematic.position = self.character.kinematic.position + self.wander_offset * self.character.kinematic.orientation_to_vector()
		self.wander_target.kinematic.position += self.wander_radius * self.wander_target.kinematic.orientation_to_vector()
		
		# Usar Face para orientar al personaje hacia el target de wander
		face = Face(
			character=self.character,
			face_target=self.wander_target,
			explicit_target=self.explicit_target
		)

		result = face.get_steering()
		# Mover al personaje hacia adelante
		result.linear = self.max_acceleration * self.character.kinematic.orientation_to_vector()
		return result