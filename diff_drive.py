import os
import pygame
import math
from pygame.math import Vector2
from generate_track import Map
from robot import Robot

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Car tutorial")
        width = 1280
        height = 810
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False

    def run(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "media", "raiju.png")
        car_image = pygame.image.load(image_path)
        resized_image = pygame.transform.scale(car_image, (36, 36)) # 36pixels -> 18cm
        robot = Robot(20, 245, 90)
        ppu = 1

        while not self.exit:
            dt = self.clock.get_time() / 1000

            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            pressed = pygame.key.get_pressed()

            # Rotations per second
            robot.motor_l.set_voltage(0)
            robot.motor_r.set_voltage(0)
            
            if pressed[pygame.K_UP]:
                robot.motor_l.set_voltage(100)
                robot.motor_r.set_voltage(100)
            elif pressed[pygame.K_DOWN]:
                robot.motor_l.set_voltage(-100)
                robot.motor_r.set_voltage(-100)

            if pressed[pygame.K_LEFT]:
                robot.motor_l.set_voltage(-80)
                robot.motor_r.set_voltage(80)
            elif pressed[pygame.K_RIGHT]:
                robot.motor_l.set_voltage(80)
                robot.motor_r.set_voltage(-80)

            robot.update(dt)
            
            #Draw
            self.screen.fill((0, 0, 0))
            map = Map(20, 245, 270, self.screen)
            map.gen_default_track()

            rotated = pygame.transform.rotate(resized_image, robot.angle)
            rect = rotated.get_rect()
            self.screen.blit(rotated, robot.position * ppu - (rect.width / 2, rect.height / 2))
            pygame.display.flip()
            self.clock.tick(self.ticks)


            
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()