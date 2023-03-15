import os
import pygame
from math import sin, radians, degrees, copysign, cos, sin
from pygame.math import Vector2


class Car:
    def __init__(self, x=50, y=50):
        self.position = Vector2(x, y)
        self.wl = 0
        self.wr = 0
        self.angle = 0
        self.velocity = Vector2(1, 0.0)
        self.angular_velocity = 0
        self.wheels_distance = 1
        self.wheel_radius = 0.2
        self.desired_wl = 0
        self.desired_wr = 0


    def update(self, dt):
        # self.velocity.x = (self.wl + self.wr) * self.wheel_radius / 2
        # self.angular_velocity = (self.wr - self.wl) * self.wheel_radius / self.wheels_distance

        # self.position += self.velocity.rotate(-self.angle) * dt
        # self.angle += degrees((self.angular_velocity) * dt)
        diff_wl = abs(self.wl - self.desired_wl)
        if diff_wl > 0.4:
            if (self.desired_wl > self.wl):
                self.wl += 0.4
            else:
                self.wl -= 0.4
        else:
            self.wl = self.desired_wl 
        
        diff_wr = abs(self.wr - self.desired_wr)
        if diff_wr > 0.4:
            if (self.desired_wr > self.wr):
                self.wr += 0.4
            else:
                self.wr -= 0.4
        else:
            self.wr = self.desired_wr 
        

        self.velocity.x = (self.wl + self.wr) * self.wheel_radius / 2
        self.angular_velocity = (self.wr - self.wl) * self.wheel_radius / self.wheels_distance

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += degrees((self.angular_velocity) * dt)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Car tutorial")
        width = 1280
        height = 720
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False

    def run(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "raiju.png")
        car_image = pygame.image.load(image_path)
        car = Car(20, 10)
        ppu = 32

        while not self.exit:
            dt = self.clock.get_time() / 1000

            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True




            pressed = pygame.key.get_pressed()

            car.desired_wl = 0
            car.desired_wr = 0
            
            if pressed[pygame.K_UP]:
                car.desired_wl = 20
                car.desired_wr = 20
            elif pressed[pygame.K_DOWN]:
                car.desired_wl = -20
                car.desired_wr = -20

            if pressed[pygame.K_LEFT]:
                car.desired_wl -= 10
                car.desired_wr += 10
            elif pressed[pygame.K_RIGHT]:
                car.desired_wl += 10
                car.desired_wr -= 10

            car.update(dt)
            
            #Draw
            self.screen.fill((0, 0, 0))
            rotated = pygame.transform.rotate(car_image, car.angle)
            rect = rotated.get_rect()
            self.screen.blit(rotated, car.position * ppu - (rect.width / 2, rect.height / 2))
            pygame.display.flip()
            self.clock.tick(self.ticks)


            
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()