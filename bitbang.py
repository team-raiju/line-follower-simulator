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
        self.ticks = 150
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
            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            dt = self.clock.get_time() / 1000

            # Line sensor
            self.screen.fill((0, 0, 0))
            self.draw_map()

            offset = Vector2(self.robot.centimeters_to_pixel(self.robot.rot_center_offset_cm), 0)

            sensor_position_1 = self.robot.position + Vector2(16, 4).rotate(-self.robot.angle) + offset.rotate(-self.robot.angle)
            sensor_position_2 = self.robot.position + Vector2(16, -4).rotate(-self.robot.angle) + offset.rotate(-self.robot.angle)
            line_sensor_1 = self.screen.get_at((int(sensor_position_1.x), int(sensor_position_1.y)))
            line_sensor_2 = self.screen.get_at((int(sensor_position_2.x), int(sensor_position_2.y)))


            is_white_1 = (line_sensor_1[0] > 150)
            is_white_2 = (line_sensor_2[0] > 150)

            
            if is_white_1:
                self.robot.motor_l.set_voltage(35)
                self.robot.motor_r.set_voltage(0)
            elif is_white_2:
                self.robot.motor_l.set_voltage(0)
                self.robot.motor_r.set_voltage(35)
            else :
                self.robot.motor_l.set_voltage(35)
                self.robot.motor_r.set_voltage(35)

            self.robot.update(dt)
            

            self.robot.display(self.screen)
            
            pygame.draw.circle(self.screen, (255, 0, 255), (sensor_position_1.x, sensor_position_1.y), 2)
            pygame.draw.circle(self.screen, (255, 0, 255), (sensor_position_2.x, sensor_position_2.y), 2)

            pygame.display.flip()
            self.clock.tick(self.ticks)


            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()