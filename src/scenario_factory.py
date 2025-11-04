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

    def create_scenario(self, scenario_type, target, path):
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
            case "KinematicArrive":
                enemies.append(NPC(
                    scenario_type,
                    100,
                    self.screen.get_width()//4,
                    self.screen.get_height()//4,
                    scenario_type
                ))
                enemies[0].set_algorithm(target=target, max_speed=100, target_radius=5.0, time_to_target=0.5)
            case "KinematicFlee":
                enemies.append(NPC(
                    scenario_type,
                    100,
                    self.screen.get_width()//4,
                    self.screen.get_height()//4,
                    scenario_type
                ))
                enemies[0].set_algorithm(target=target, max_speed=30)
            case "KinematicWander":
                for _ in range(5):
                    enemies.append(NPC(
                        scenario_type,
                        100,
                        random.randint(0, self.screen.get_width()),
                        random.randint(0, self.screen.get_height()),
                        scenario_type
                    ))
                    enemies[-1].kinematic.orientation = random.randint(0, 360)
                    enemies[-1].set_algorithm(max_speed=80, max_rotation=250)
            case "DynamicSeek":
                enemies.append(NPC(
                    scenario_type,
                    100,
                    self.screen.get_width()//4,
                    self.screen.get_height()//4,
                    scenario_type
                ))
                enemies[0].set_algorithm(target=target, max_acceleration=150)
            case "DynamicArrive":
                enemies.append(NPC(
                    scenario_type,
                    100,
                    self.screen.get_width()//4,
                    self.screen.get_height()//4,
                    scenario_type
                ))
                enemies[0].set_algorithm(target=target, max_acceleration=150, max_speed=120, target_radius=5.0, slow_radius=100.0, time_to_target=0.1)
            case "DynamicFlee":
                enemies.append(NPC(
                    scenario_type,
                    100,
                    self.screen.get_width()//2-50,
                    self.screen.get_height()//2-50,
                    scenario_type
                ))
                enemies[0].set_algorithm(target=target, max_acceleration=20)
            case "Align":
                enemies.append(NPC(
                    scenario_type,
                    100,
                    self.screen.get_width()//4,
                    self.screen.get_height()//4,
                    scenario_type
                ))
                enemies[0].set_algorithm(target=target, max_rotation=90, max_angular_acceleration=80, target_radius=0.5, slow_radius=50, time_to_target=0.1)
            case "VelocityMatch":
                enemies.append(NPC(
                    scenario_type,
                    100,
                    self.screen.get_width()//4,
                    self.screen.get_height()//4,
                    scenario_type
                ))
                enemies[0].set_algorithm(target=target, max_acceleration=50, time_to_target=0.1)
            case "Pursue":
                enemies.append(NPC(
                    scenario_type,
                    100,
                    self.screen.get_width()//4,
                    self.screen.get_height()//4,
                    scenario_type
                ))
                enemies[0].set_algorithm(pursue_target=target, max_prediction=3, explicit_target=Player("Target", 0, 0, 0))
            case "Evade":
                enemies.append(NPC(
                    scenario_type,
                    100,
                    self.screen.get_width()//2-50,
                    self.screen.get_height()//2-50,
                    scenario_type
                ))
                enemies[0].set_algorithm(evade_target=target, max_prediction=3, explicit_target=Player("Target", 0, 0, 0))
            case "Face":
                num_npcs = 10
                radius = 150
                player_pos = target.kinematic.position

                # Distribuir NPCs en un círculo alrededor del jugador
                for i in range(num_npcs):
                    angle = (2 * math.pi / num_npcs) * i
                    
                    enemies.append(NPC(
                        f"Face-{i+1}",
                        100,
                        player_pos.x + radius * math.cos(angle),
                        player_pos.y + radius * math.sin(angle),
                        scenario_type
                    ))
                    enemies[-1].kinematic.orientation = random.randint(0, 360)
                    enemies[-1].set_algorithm(face_target=target, explicit_target=Player("Target", 0, 0, 0))
            case "BlendedSteeringLWYG":
                enemies.append(NPC(
                    "LWYG+Pursue",
                    100,
                    self.screen.get_width()//4,
                    self.screen.get_height()//4,
                    scenario_type
                ))
                # Comportamientos a combinar
                pursue_movement_behavior = {
                    "Pursue": {"max_prediction": 0.5, "pursue_target": target},
                }
                enemies[-1].set_algorithm(movement_behavior=pursue_movement_behavior, explicit_target=Player("Target", 0, 0, 0))

                enemies.append(NPC(
                    "LWYG+Evade",
                    100,
                    self.screen.get_width()//2,
                    self.screen.get_height()//2,
                    scenario_type
                ))
                # Comportamientos a combinar
                evade_movement_behavior = {
                    "Evade": {"max_prediction": 0.5, "evade_target": target}
                }
                enemies[-1].set_algorithm(movement_behavior=evade_movement_behavior, explicit_target=Player("Target", 0, 0, 0))
            case "FollowPath":
                path_points = path.get_path()
                # Calcular el bounding box del camino para posicionar NPCs dentro y fuera
                min_x = min(point.x for point in path_points)
                max_x = max(point.x for point in path_points)
                min_y = min(point.y for point in path_points)
                max_y = max(point.y for point in path_points)

                path_box = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

                num_npc_inside = 2
                num_npc_outside = 3
                for i in range(num_npc_inside):
                    enemies.append(NPC(
                        f"Inside-{i+1}",
                        100,
                        random.uniform(path_box.left, path_box.right),
                        random.uniform(path_box.top, path_box.bottom),
                        scenario_type
                    ))
                    enemies[-1].kinematic.orientation = random.randint(0, 360)
                    enemies[-1].set_algorithm(path=path, explicit_target=Player("Target", 0, 0, 0))
                
                for i in range(num_npc_outside):
                    pos_x, pos_y = 0, 0
                    # Repetir hasta encontrar un punto que esté fuera del bounding box
                    while True:
                        pos_x = random.randint(0, self.screen.get_width())
                        pos_y = random.randint(0, self.screen.get_height())
                        # collidepoint comprueba si un punto está dentro de un Rect
                        if not path_box.collidepoint(pos_x, pos_y):
                            break
                    
                    enemies.append(NPC(
                        f"Outside-{i+1}",
                        100,
                        pos_x,
                        pos_y,
                        scenario_type
                    ))
                    enemies[-1].kinematic.orientation = random.randint(0, 360)
                    enemies[-1].set_algorithm(path=path, explicit_target=Player("Target", 0, 0, 0))
            case "DynamicWander":
                for _ in range(5):
                    enemies.append(NPC(
                        scenario_type,
                        100,
                        random.randint(0, self.screen.get_width()),
                        random.randint(0, self.screen.get_height()),
                        scenario_type
                    ))
                    enemies[-1].kinematic.orientation = random.randint(0, 360)
                    enemies[-1].set_algorithm(max_acceleration=80, wander_target=Player("WanderTarget", 0, 0, 0), explicit_target=Player("Target", 0, 0, 0))
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
