# src/scenario_factory.py
import random
import math
import pygame
from imports.npc.npc import NPC
from imports.player.player import Player
from imports.map.path import Path

class ScenarioFactory:
    def __init__(self, screen, game_map):
        self.screen = screen
        self.game_map = game_map

    def create_scenario(self, scenario_type, target):
        enemies = []
        uses_rotation = scenario_type in ["Align", "VelocityMatch", "Face", "DynamicWander", "BlendedSteeringLWYG", "PrioritySteering"]
        
        # This is a simplified version. In a real scenario, you would move all cases from the old gui.py here.
        # For now, let's just implement one case to show the structure.
        match scenario_type:
            case "KinematicSeek":
                enemies.append(NPC(
                    scenario_type,
                    100,
                    self.screen.get_width()//4,
                    self.screen.get_height()//4,
                    scenario_type
                ))
                enemies[0].set_algorithm(target=target, max_speed=80)
            case "PrioritySteering":
                # Obstacles are now loaded from the map
                obstacles = self.game_map.obstacles

                enemies.append(NPC(
                    "LWYG+Pursue",
                    100,
                    self.screen.get_width()//4,
                    self.screen.get_height()//4,
                    scenario_type
                ))
                pursue_movement_behavior = {
                    "Pursue": {"max_prediction": 0.5, "pursue_target": target},
                }
                behaviors = {
                    "ObstacleAvoidance": {
                        "obstacles": obstacles,
                        "explicit_target": Player("AvoidTarget", 0, 0, 0),
                        "avoid_distance": 100,
                        "lookahead": 100,
                        "max_acceleration": 80
                    },
                    "BlendedSteeringLWYG": {
                        "movement_behavior": pursue_movement_behavior,
                        "explicit_target": Player("Target", 0, 0, 0)
                    }
                }
                enemies[0].set_algorithm(behaviors=behaviors)
            # ... other cases would go here
            case _:
                # Default case or error handling
                print(f"Scenario '{scenario_type}' not implemented in factory.")

        return enemies, uses_rotation
