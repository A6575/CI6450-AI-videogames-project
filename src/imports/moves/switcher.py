from imports.moves.kinematic_seek import KinematicSeek
from imports.moves.kinematic_arrive import KinematicArrive
from imports.moves.kinematic_flee import KinematicFlee
from imports.moves.kinematic_wander import KinematicWander
from imports.moves.dynamic_seek import DynamicSeek
from imports.moves.dynamic_arrive import DynamicArrive
from imports.moves.dynamic_flee import DynamicFlee
from imports.moves.align import Align
from imports.moves.velocity_match import VelocityMatch
from imports.moves.pursue import Pursue
from imports.moves.evade import Evade
from imports.moves.face import Face

SWITCHER_ALGORITHMS = {
	"KinematicSeek": KinematicSeek,
	"KinematicArrive": KinematicArrive,
	"KinematicFlee": KinematicFlee,
	"KinematicWander": KinematicWander,
	"DynamicSeek": DynamicSeek,
	"DynamicArrive": DynamicArrive,
	"DynamicFlee": DynamicFlee,
	"Align": Align,
	"VelocityMatch": VelocityMatch,
	"Pursue": Pursue,
	"Evade": Evade,
	"Face": Face,
}