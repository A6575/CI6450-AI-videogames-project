from abc import ABC, abstractmethod

class State(ABC):
	def __init__(self, npc):
		self.npc = npc

	@abstractmethod
	def enter(self, **kwargs):
		pass

	@abstractmethod
	def execute(self, dt, **kwargs):
		pass

	@abstractmethod
	def exit(self):
		pass

class StateMachine:
	def __init__(self, initial_state):
		self.current_state = initial_state
		if self.current_state:
			self.current_state.enter()

	def change_state(self, new_state, **kwargs):
		if self.current_state:
			self.current_state.exit()
		self.current_state = new_state
		if self.current_state:
			self.current_state.enter(**kwargs)
	
	def update(self, dt, **kwargs):
		if self.current_state:
			self.current_state.execute(dt, **kwargs)