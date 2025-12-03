class Blackboard:
    """
    Pizarra compartida para coordinación (Blackboard pattern)
    """
    def __init__(self):
        self.data = {
            "player_last_known_pos": None,
            "player_health": None
        }