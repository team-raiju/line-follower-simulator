import os
import pygame
from pygame.math import Vector2
from generate_track import Map
from load_track import LoadMap
from robot import Robot

MAP_FILE_NAME = "map5.png"
MAP_WIDTH_CM = 651
MAP_HEIGHT_CM = 317
MAP_MARGIN_CM = 25
MAP_CM_PER_PIXELS = 2

ROBOT_INIT_POS_X_CM = 150 
ROBOT_INIT_POS_Y_CM = 334
ROBOT_INIT_ANGLE = 180
MIN_LEFT_MARKER_COUNTER = 30

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
        self.ticks = 150
        self.exit = False

        self.robot = Robot(MAP_CM_PER_PIXELS, ROBOT_SIZE_X_CM,           \
                        ROBOT_SIZE_Y_CM, ROTATION_OFFSET_FROM_CENTER_CM, \
                        WHEELS_DIST_CM, WHEELS_RADIUS_CM,                \
                        ROBOT_INIT_POS_X_CM, ROBOT_INIT_POS_Y_CM,        \
                        ROBOT_INIT_ANGLE, ROBOT_IMAGE)
    

        self.map = LoadMap(self.screen)
        self.map.load_map_from_file(MAP_FILE_NAME, margin_pixels, self.map_width_pixels, self.map_height_pixels)

        self.left_marker_counter = 0
        self.right_marker_counter = 0
        self.base_speed = 80
        self.last_error = 0
        self.kp = 28
        self.kd = 15 
    
    def draw_map(self):
        self.map.draw_loaded_map()
    

    def run(self):
        time = 0
        while not self.exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            dt = self.clock.get_time() / 1000
            time += dt 

            self.screen.fill((0, 0, 0))
            self.draw_map()

            line_sensor = self.robot.get_line_sensor(self.screen, self.screen_width, self.screen_height)

            # filter line
            if (line_sensor[7] == 0 or line_sensor[8] == 0 or line_sensor[6] == 0 or line_sensor[9] == 0):
                line_sensor[15] = 0
                line_sensor[14] = 0
                line_sensor[0] = 0
                line_sensor[1] = 0

            # print(line_sensor)
            error = 2.50 * (line_sensor[15] - line_sensor[0]) + \
                    2.25 * (line_sensor[14] - line_sensor[1]) + \
                    2.00 * (line_sensor[13] - line_sensor[2]) + \
                    1.75 * (line_sensor[12] - line_sensor[3]) + \
                    1.50 * (line_sensor[11] - line_sensor[4]) + \
                    1.25 * (line_sensor[10] - line_sensor[5]) + \
                    1.00 * (line_sensor[9] - line_sensor[6])  + \
                    0.75 * (line_sensor[8] - line_sensor[7])
            
            
            
            derivative = (error - self.last_error)
            self.robot.motor_l.set_voltage(self.base_speed - (error * self.kp + derivative * self.kd))
            self.robot.motor_r.set_voltage(self.base_speed + (error * self.kp + derivative * self.kd))
            
            self.last_error = error
            self.robot.update(dt)

            # Count markers
            left_marker = line_sensor[16] == 0 or line_sensor[17] == 0
            right_marker = line_sensor[18] == 0 or line_sensor[19] == 0
            if (left_marker and not self.last_left_marker):
                self.left_marker_counter += 1
                print("Left marker - " + str(self.left_marker_counter))

            if (right_marker and not self.last_right_marker):
                self.right_marker_counter += 1
                print("Right marker - " + str(self.right_marker_counter))

                if (self.right_marker_counter == 1):
                    time = 0

                if (self.left_marker_counter > MIN_LEFT_MARKER_COUNTER):
                    print("Total time: " + str(round(time, 4)) + "s")

                    self.base_speed = 15
                    self.kd = 0
                    self.kp = 0



            self.last_left_marker = left_marker
            self.last_right_marker = right_marker
            
            #Draw
            self.robot.display(self.screen)
            # self.robot.display_line_sensor(self.screen)
            pygame.display.flip()

            self.clock.tick(self.ticks)


            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()