import os
import pygame
import math
from pygame.math import Vector2
from generate_track import Map
from load_track import LoadMap
from robot import Robot

MAP_FILE_NAME = "map2.png"
MAP_WIDTH_CM = 186
MAP_HEIGHT_CM = 354
MAP_MARGIN_CM = 25
MAP_CM_PER_PIXELS = 6

ROBOT_INIT_POS_X_CM = 202 
ROBOT_INIT_POS_Y_CM = 100
ROBOT_INIT_ANGLE = 270

ROBOT_IMAGE = "robot-img.png"
ROBOT_SIZE_X_CM = 14.0 # Width
ROBOT_SIZE_Y_CM = 14.0 # Height
ROTATION_OFFSET_FROM_CENTER_CM = 4.73
WHEELS_DIST_CM = 14.0
WHEELS_RADIUS_CM = 1.0

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Line Follower")

        self.map_width_pixels = MAP_WIDTH_CM * MAP_CM_PER_PIXELS
        self.map_height_pixels = MAP_HEIGHT_CM * MAP_CM_PER_PIXELS

        margin_pixels = MAP_MARGIN_CM * MAP_CM_PER_PIXELS
        self.screen_width = self.map_width_pixels + (2 * margin_pixels)
        self.screen_height = self.map_height_pixels + (2 * margin_pixels)

        self.screen = pygame.display.set_mode((self.screen_width , self.screen_height))
        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False
        self.last_error = 0

        self.robot = Robot(MAP_CM_PER_PIXELS, ROBOT_SIZE_X_CM,           \
                        ROBOT_SIZE_Y_CM, ROTATION_OFFSET_FROM_CENTER_CM, \
                        WHEELS_DIST_CM, WHEELS_RADIUS_CM,                \
                        ROBOT_INIT_POS_X_CM, ROBOT_INIT_POS_Y_CM,        \
                        ROBOT_INIT_ANGLE, ROBOT_IMAGE)
    
        self.map = LoadMap(self.screen)
        self.map.load_map_from_file(MAP_FILE_NAME, margin_pixels, self.map_width_pixels, self.map_height_pixels)


    def draw_map(self):
        self.map.draw_loaded_map()
        
    def run(self):
        while not self.exit:
            dt = self.clock.get_time() / 1000

            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            pressed = pygame.key.get_pressed()

            # Rotations per second
            self.robot.motor_l.set_voltage(0)
            self.robot.motor_r.set_voltage(0)
            
            if pressed[pygame.K_UP]:
                self.robot.motor_l.set_voltage(40)
                self.robot.motor_r.set_voltage(40)
            elif pressed[pygame.K_DOWN]:
                self.robot.motor_l.set_voltage(-40)
                self.robot.motor_r.set_voltage(-40)

            if pressed[pygame.K_LEFT]:
                self.robot.motor_l.set_voltage(-30)
                self.robot.motor_r.set_voltage(30)
            elif pressed[pygame.K_RIGHT]:
                self.robot.motor_l.set_voltage(30)
                self.robot.motor_r.set_voltage(-30)

            self.robot.update(dt)
            
            #Draw
            self.screen.fill((0, 0, 0))
            self.draw_map()
            # line_sensor = self.robot.get_line_sensor(self.screen, self.screen_width, self.screen_height)
            # print(line_sensor)

            self.robot.display(self.screen)
            self.robot.display_line_sensor(self.screen)


            pygame.display.flip()
            self.clock.tick(self.ticks)


            
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()