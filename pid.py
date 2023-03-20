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
            sensor_position_1 = robot.position + Vector2(20, 3).rotate(-robot.angle)
            sensor_position_2 = robot.position + Vector2(20, -3).rotate(-robot.angle)
            sensor_position_3 = robot.position + Vector2(20, 6).rotate(-robot.angle)
            sensor_position_4 = robot.position + Vector2(20, -6).rotate(-robot.angle)
            sensor_position_5 = robot.position + Vector2(20, 8).rotate(-robot.angle)
            sensor_position_6 = robot.position + Vector2(20, -8).rotate(-robot.angle)
            line_sensor_1 = self.screen.get_at((int(sensor_position_1.x), int(sensor_position_1.y)))
            line_sensor_2 = self.screen.get_at((int(sensor_position_2.x), int(sensor_position_2.y)))
            line_sensor_3 = self.screen.get_at((int(sensor_position_3.x), int(sensor_position_3.y)))
            line_sensor_4 = self.screen.get_at((int(sensor_position_4.x), int(sensor_position_4.y)))
            line_sensor_5 = self.screen.get_at((int(sensor_position_5.x), int(sensor_position_5.y)))
            line_sensor_6 = self.screen.get_at((int(sensor_position_6.x), int(sensor_position_6.y)))

            is_black_1 = (line_sensor_1[0] != 255)
            is_black_2 = (line_sensor_2[0] != 255)
            is_black_3 = (line_sensor_3[0] != 255)
            is_black_4 = (line_sensor_4[0] != 255)
            is_black_5 = (line_sensor_5[0] != 255)
            is_black_6 = (line_sensor_6[0] != 255)

            error = is_black_1 + 2 * is_black_3 + 3 * is_black_5 - (is_black_2 + 2 * is_black_4 + 3 * is_black_6)
            kp = 3

            robot.motor_l.set_voltage(40 - error * kp)
            robot.motor_r.set_voltage(40 + error * kp)
            

            robot.update(dt)
            
            #Draw
            self.screen.fill((0, 0, 0))
            map = Map(20, 245, 270, self.screen)
            map.gen_default_track()

            line_sensor_draw_1 = sensor_position_1 + Vector2(5, 0).rotate(-robot.angle)
            line_sensor_draw_2 = sensor_position_2 + Vector2(5, 0).rotate(-robot.angle)
            line_sensor_draw_3 = sensor_position_3 + Vector2(5, 0).rotate(-robot.angle)
            line_sensor_draw_4 = sensor_position_4 + Vector2(5, 0).rotate(-robot.angle)
            line_sensor_draw_5 = sensor_position_5 + Vector2(5, 0).rotate(-robot.angle)
            line_sensor_draw_6 = sensor_position_6 + Vector2(5, 0).rotate(-robot.angle)
            pygame.draw.circle(self.screen, (255, 0, 255), (line_sensor_draw_1.x, line_sensor_draw_1.y), 2)
            pygame.draw.circle(self.screen, (255, 0, 255), (line_sensor_draw_2.x, line_sensor_draw_2.y), 2)
            pygame.draw.circle(self.screen, (255, 0, 255), (line_sensor_draw_3.x, line_sensor_draw_3.y), 2)
            pygame.draw.circle(self.screen, (255, 0, 255), (line_sensor_draw_4.x, line_sensor_draw_4.y), 2)
            pygame.draw.circle(self.screen, (255, 0, 255), (line_sensor_draw_5.x, line_sensor_draw_5.y), 2)
            pygame.draw.circle(self.screen, (255, 0, 255), (line_sensor_draw_6.x, line_sensor_draw_6.y), 2)

            rotated = pygame.transform.rotate(resized_image, robot.angle)
            rect = rotated.get_rect()
            self.screen.blit(rotated, robot.position- (rect.width / 2, rect.height / 2))
            pygame.display.flip()
            self.clock.tick(self.ticks)


            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()