# Codigo principal del proyecto
from imports.gui import GUI

if __name__ == "__main__":
	gui = GUI()
	gui.run(
		draw_path=False, 
		scenario_type="KinematicArrive",
		draw_obstacles=False
	)