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
MAP_CM_PER_PIXELS = 2
ROBOT_SIZE_X_CM = 14 # Width
ROBOT_SIZE_Y_CM = 14 # Height
ROBOT_INIT_POS_X_CM = 202 
ROBOT_INIT_POS_Y_CM = 100
ROBOT_INIT_ANGLE = 270

ROTATION_OFFSET_FROM_CENTER_CM = 4.73

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

        current_dir = os.path.dirname(os.path.abspath(__file__))
        robot_image_path = os.path.join(current_dir, "media" , "robot-img.png")
        robot_image = pygame.image.load(robot_image_path)

        self.robot = Robot(MAP_CM_PER_PIXELS, ROBOT_INIT_POS_X_CM, ROBOT_INIT_POS_Y_CM, ROBOT_INIT_ANGLE)
        self.resized_robot_img = pygame.transform.scale(robot_image, (self.robot.centimeters_to_pixel(ROBOT_SIZE_Y_CM), self.robot.centimeters_to_pixel(ROBOT_SIZE_X_CM)))

        self.map = LoadMap(self.screen)
        self.map.load_map_from_file(MAP_FILE_NAME, margin_pixels, self.map_width_pixels, self.map_height_pixels)

    def rotate(self, angle, pivot, offset):
        rotated_image = pygame.transform.rotozoom(self.resized_robot_img, -angle, 1)  
        rotated_offset = offset.rotate(angle)  
        rect = rotated_image.get_rect(center = pivot + rotated_offset)
        return rotated_image, rect 

    def draw_robot(self):
        robot_center = self.robot.position
        offset = Vector2(ROTATION_OFFSET_FROM_CENTER_CM * MAP_CM_PER_PIXELS, 0)
        rotated_image, rect = self.rotate(-self.robot.angle, robot_center, offset)
        self.screen.blit(rotated_image, rect)  # Blit the rotated image.
        pygame.draw.circle(self.screen, (30, 250, 70), robot_center, 3)  # Pivot point.
        pygame.draw.rect(self.screen, (30, 250, 70), rect, 1)  # The rect.
        pygame.display.flip()

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
                self.robot.motor_l.set_voltage(80)
                self.robot.motor_r.set_voltage(80)
            elif pressed[pygame.K_DOWN]:
                self.robot.motor_l.set_voltage(-80)
                self.robot.motor_r.set_voltage(-80)

            if pressed[pygame.K_LEFT]:
                self.robot.motor_l.set_voltage(-60)
                self.robot.motor_r.set_voltage(60)
            elif pressed[pygame.K_RIGHT]:
                self.robot.motor_l.set_voltage(60)
                self.robot.motor_r.set_voltage(-60)

            self.robot.update(dt)
            
            #Draw
            self.screen.fill((0, 0, 0))
            self.draw_map()
            self.draw_robot()

            pygame.display.flip()
            self.clock.tick(self.ticks)


            
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()