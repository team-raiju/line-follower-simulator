import os
import pygame
from pygame.math import Vector2
from generate_track import Map
from load_track import LoadMap
from robot import Robot

MAP_FILE_NAME = "map1.png"
MAP_WIDTH_CM = 230
MAP_HEIGHT_CM = 395
MAP_MARGIN_CM = 25
MAP_CM_PER_PIXELS = 2

ROBOT_INIT_POS_X_CM = 36 
ROBOT_INIT_POS_Y_CM = 150
ROBOT_INIT_ANGLE = 90
MIN_LEFT_MARKER_COUNTER = 20

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
        self.ticks = 180
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
        self.last_left_marker = False
        self.last_right_marker = False
        self.last_error = 0
        
        self.base_speed = 100
        self.kp = 43
        self.kd = 60
    
    def draw_map(self):
        self.map.draw_loaded_map()
    
    def draw_timer(self, time):
        text_surface = pygame.font.Font(None, 36).render("Time: " + "{:.3f}s".format(time), True, (255, 0, 0))
        self.screen.blit(text_surface, (10, 10))

    def calc_error(self, line_sensor_val: list):
        # Similar to center of mass calculation
        num_half_sensors = int(8)
        count_left = 0
        count_right = 0
        sum_left = 0
        sum_right = 0
        for i in range (num_half_sensors):
            count_left += line_sensor_val[i]
            count_right += line_sensor_val[num_half_sensors + i]

            sum_left += i * line_sensor_val[num_half_sensors - 1 - i]
            sum_right += i * line_sensor_val[num_half_sensors + i]

        if count_left == 0:
            count_left = 1
        if count_right == 0:
            count_right = 1
        pos_left = sum_left / count_left
        pos_right = sum_right / count_right

        return (pos_left - pos_right)

    def run(self):
        time = 0
        finished = False
        while not self.exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            dt = self.clock.get_time() / 1000
            if (not finished):
                time += dt 

            self.screen.fill((0, 0, 0))
            self.draw_map()
            self.draw_timer(time)


            line_sensor = self.robot.get_line_sensor(self.screen, self.screen_width, self.screen_height)

            # filter line
            if (line_sensor[7] == 0 or line_sensor[8] == 0 or line_sensor[6] == 0 or line_sensor[9] == 0):
                line_sensor[15] = 0
                line_sensor[14] = 0
                line_sensor[0] = 0
                line_sensor[1] = 0

            # print(line_sensor)
            error = self.calc_error(line_sensor)
            
            derivative = (error - self.last_error)
            l_speed = self.base_speed - (error * self.kp + derivative * self.kd)
            r_speed = self.base_speed + (error * self.kp + derivative * self.kd)
            self.robot.motor_l.set_voltage(l_speed)
            self.robot.motor_r.set_voltage(r_speed)
            
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
                    finished = True

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