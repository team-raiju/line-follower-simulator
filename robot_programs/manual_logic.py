import pygame
from .base_logic import RobotLogic

class ManualLogic(RobotLogic):
    def __init__(self, **kwargs):
        self.time = 0.0
        self.fwd_speed = kwargs.get('fwd_speed', 40)
        self.turn_speed = kwargs.get('turn_speed', 30)
        print(f"ManualLogic initialized. Use arrow keys to drive.")
        print(f"Fwd/Back Speed: {self.fwd_speed}, Turn Speed: {self.turn_speed}")

    def process_tick(self, dt: float, line_sensor_data: list, robot_state: dict):
        self.time += dt
        
        pressed = pygame.key.get_pressed()
        
        l_speed = 0.0
        r_speed = 0.0

        if pressed[pygame.K_UP]:
            l_speed = self.fwd_speed
            r_speed = self.fwd_speed
        elif pressed[pygame.K_DOWN]:
            l_speed = -self.fwd_speed
            r_speed = -self.fwd_speed
        elif pressed[pygame.K_LEFT]:
            l_speed = -self.turn_speed
            r_speed = self.turn_speed
        elif pressed[pygame.K_RIGHT]:
            l_speed = self.turn_speed
            r_speed = -self.turn_speed
            
        return l_speed, r_speed

    def get_time(self) -> float:
        return self.time

    def first_right_marker(self) -> bool:
        return False