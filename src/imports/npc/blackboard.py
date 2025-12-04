# Clase pizarra compartida para NPCs
# Su funcion es almacenar informacion relevante para la toma de decisiones
# o coordinacion entre NPCs.
class Blackboard:
    """
    Pizarra compartida para coordinación (Blackboard pattern)
    """
    def __init__(self):
        self.data = {
            "player_last_known_pos": None,
            "player_health": None
        }