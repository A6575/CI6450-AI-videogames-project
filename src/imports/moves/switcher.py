from imports.moves.kinematic_seek import KinematicSeek
from imports.moves.kinematic_arrive import KinematicArrive
from imports.moves.kinematic_flee import KinematicFlee
from imports.moves.kinematic_wander import KinematicWander
from imports.moves.dynamic_seek import DynamicSeek

SWITCHER_ALGORITHMS = {
	"KinematicSeek": KinematicSeek,
	"KinematicArrive": KinematicArrive,
	"KinematicFlee": KinematicFlee,
	"KinematicWander": KinematicWander,
	"DynamicSeek": DynamicSeek,
}