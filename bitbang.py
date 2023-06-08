import os
import pygame
from pygame.math import Vector2
from generate_track import Map
from load_track import LoadMap
from robot import Robot

MAP_FILE_NAME = "map4.png"
MAP_WIDTH_CM = 478
MAP_HEIGHT_CM = 310
MAP_MARGIN_CM = 25
MAP_CM_PER_PIXELS = 2.5

ROBOT_SIZE_X_CM = 12
ROBOT_SIZE_Y_CM = 6
ROBOT_INIT_POS_X_CM = 33 
ROBOT_INIT_POS_Y_CM = 180
ROBOT_INIT_ANGLE = 90

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
        robot_image_path = os.path.join(current_dir, "media" , "raiju.png")
        robot_image = pygame.image.load(robot_image_path)

        self.robot = Robot(MAP_CM_PER_PIXELS, ROBOT_INIT_POS_X_CM, ROBOT_INIT_POS_Y_CM, ROBOT_INIT_ANGLE)
        self.resized_robot_img = pygame.transform.scale(robot_image, (self.robot.centimeters_to_pixel(ROBOT_SIZE_Y_CM), self.robot.centimeters_to_pixel(ROBOT_SIZE_X_CM)))

        self.map = LoadMap(self.screen)
        self.map.load_map_from_file(MAP_FILE_NAME, margin_pixels, self.map_width_pixels, self.map_height_pixels)

    def draw_robot(self):
        rotated = pygame.transform.rotate(self.resized_robot_img, self.robot.angle)
        rect = rotated.get_rect()
        self.screen.blit(rotated, self.robot.position - (rect.width / 2, rect.height / 2))

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
            sensor_position_1 = self.robot.position + Vector2(20, 5).rotate(-self.robot.angle)
            sensor_position_2 = self.robot.position + Vector2(20, -5).rotate(-self.robot.angle)
            line_sensor_1 = self.screen.get_at((int(sensor_position_1.x), int(sensor_position_1.y)))
            line_sensor_2 = self.screen.get_at((int(sensor_position_2.x), int(sensor_position_2.y)))

            is_white_1 = (line_sensor_1[0] > 240)
            is_white_2 = (line_sensor_2[0] > 240)
            
            if is_white_1:
                self.robot.motor_l.set_voltage(30)
                self.robot.motor_r.set_voltage(0)
            elif is_white_2:
                self.robot.motor_l.set_voltage(0)
                self.robot.motor_r.set_voltage(30)
            else :
                self.robot.motor_l.set_voltage(30)
                self.robot.motor_r.set_voltage(30)

            self.robot.update(dt)
            
            #Draw
            self.screen.fill((0, 0, 0))
            self.draw_map()
            self.draw_robot()


            line_sensor_draw_1 = sensor_position_1 + Vector2(5, 0).rotate(-self.robot.angle)
            line_sensor_draw_2 = sensor_position_2 + Vector2(5, 0).rotate(-self.robot.angle)
            pygame.draw.circle(self.screen, (255, 0, 255), (line_sensor_draw_1.x, line_sensor_draw_1.y), 2)
            pygame.draw.circle(self.screen, (255, 0, 255), (line_sensor_draw_2.x, line_sensor_draw_2.y), 2)

            pygame.display.flip()
            self.clock.tick(self.ticks)


            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()