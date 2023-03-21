import os
import pygame
from pygame.math import Vector2
from generate_track import Map
from robot import Robot

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Line Follower")
        width = 1280
        height = 810
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False
        self.last_error = 0

    def run(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "raiju.png")
        robot_image = pygame.image.load(image_path)
        resized_image = pygame.transform.scale(robot_image, (36, 36))
        robot = Robot(20, 245, 90)

        while not self.exit:
            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            dt = self.clock.get_time() / 1000

            # Line sensor
            line_sensor = robot.get_line_sensor(self.screen, 1280, 810)
            # print(line_sensor)

            kp = 6
            kd = 0.001
            
            error = 3 * (line_sensor[5] - line_sensor[0]) + 2 * (line_sensor[4] -line_sensor[1]) + (line_sensor[3] - line_sensor[2])
            derivative = kd * (error - self.last_error)

            robot.motor_l.set_voltage(42 - (error * kp + derivative * kd))
            robot.motor_r.set_voltage(42 + (error * kp + derivative * kd))

            self.last_error = error
            

            robot.update(dt)
            
            #Draw
            self.screen.fill((0, 0, 0))
            map = Map(20, 245, 270, self.screen)
            map.gen_default_track()

            for sensor in robot.line_sensor_pos:
                sensor_position = robot.position + robot.centimeters_to_pixel(sensor).rotate(-robot.angle)
                line_sensor_draw = sensor_position + Vector2(3, 0).rotate(-robot.angle)
                pygame.draw.circle(self.screen, (255, 0, 255), (line_sensor_draw.x, line_sensor_draw.y), 1)


            rotated = pygame.transform.rotate(resized_image, robot.angle)
            rect = rotated.get_rect()
            self.screen.blit(rotated, robot.position- (rect.width / 2, rect.height / 2))
            pygame.display.flip()
            self.clock.tick(self.ticks)


            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()