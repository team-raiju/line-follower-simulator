import os
import pygame
from pygame.math import Vector2
from generate_track import Map
from robot import Robot

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Line Follower")

        self.map_name = "map1.png"

        self.map_width_cm = 545
        self.map_height_cm = 595
        self.cm_per_pixel = 1.5

        self.map_width_pixels = self.map_width_cm * self.cm_per_pixel
        self.map_height_pixels = self.map_height_cm * self.cm_per_pixel
        self.margin_pixels = 40

        self.screen_width = self.map_width_pixels + (2 * self.margin_pixels)
        self.screen_height = self.map_height_pixels + (2 * self.margin_pixels)

        self.screen = pygame.display.set_mode((self.screen_width , self.screen_height))
        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False
        self.last_error = 0

        current_dir = os.path.dirname(os.path.abspath(__file__))
        robot_image_path = os.path.join(current_dir, "media" , "raiju.png")
        robot_image = pygame.image.load(robot_image_path)
        robot_size_x_cm = 12
        robot_size_y_cm = 6
        robot_init_x_cm = 200
        robot_init_y_cm = 40
        robot_init_angle = 0

        self.robot = Robot(self.cm_per_pixel, robot_init_x_cm, robot_init_y_cm, robot_init_angle)
        self.resized_robot_img = pygame.transform.scale(robot_image, (self.robot.centimeters_to_pixel(robot_size_y_cm), self.robot.centimeters_to_pixel(robot_size_x_cm)))
    
    def draw_line_sensor(self):
        for sensor in self.robot.line_sensor_pos:
                sensor_position = self.robot.position + self.robot.centimeters_to_pixel(sensor).rotate(-self.robot.angle)
                line_sensor_draw = sensor_position + Vector2(3, 0).rotate(-self.robot.angle)
                pygame.draw.circle(self.screen, (255, 0, 255), (line_sensor_draw.x, line_sensor_draw.y), 1)

    def draw_robot(self):
            rotated = pygame.transform.rotate(self.resized_robot_img, self.robot.angle)
            rect = rotated.get_rect()
            self.screen.blit(rotated, self.robot.position- (rect.width / 2, rect.height / 2))

    def draw_map(self):
        map = Map(self.screen, self.cm_per_pixel)
        map.load_map_from_file("map3.png", self.margin_pixels, self.map_width_pixels, self.map_height_pixels)

    def run(self):

        while not self.exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            dt = self.clock.get_time() / 1000

            line_sensor = self.robot.get_line_sensor(self.screen, self.screen_width, self.screen_height)
            # print(line_sensor)
            error = 1.5 * (line_sensor[7] - line_sensor[4]) + 3 * (line_sensor[9] - line_sensor[2]) + 2 * (line_sensor[8] -line_sensor[3]) + (line_sensor[6] - line_sensor[5])
            
            kp = 4.5
            kd = 0.001
            base_speed = 38
            
            derivative = kd * (error - self.last_error)
            self.robot.motor_l.set_voltage(base_speed - (error * kp + derivative * kd))
            self.robot.motor_r.set_voltage(base_speed + (error * kp + derivative * kd))
            
            self.last_error = error
            self.robot.update(dt)
            
            #Draw
            self.screen.fill((0, 0, 0))

            self.draw_map()
            self.draw_line_sensor()
            self.draw_robot()
            pygame.display.flip()

            self.clock.tick(self.ticks)


            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()