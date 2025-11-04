# Codigo principal del proyecto
from imports.gui import GUI
from game import Game
if __name__ == "__main__":
	game = Game()
	game.run(
		scenario_type="DynamicArrive"
	)