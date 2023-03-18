import os
import pygame
import math
from pygame.math import Vector2
from generate_track import Map

class Car:
    def __init__(self, x=50, y=50):
        self.position = Vector2(x, y)
        self.wl = 0
        self.wr = 0
        self.angle = 90
        self.velocity = Vector2(1, 0.0)
        self.angular_velocity = 0
        self.wheels_distance = 64
        self.wheel_radius = 6.4
        self.desired_wl = 0
        self.desired_wr = 0


    def update(self, dt):
        diff_wl = abs(self.wl - self.desired_wl)
        if diff_wl > 6:
            if (self.desired_wl > self.wl):
                self.wl += 6
            else:
                self.wl -= 6
        else:
            self.wl = self.desired_wl 
        
        diff_wr = abs(self.wr - self.desired_wr)
        if diff_wr > 6:
            if (self.desired_wr > self.wr):
                self.wr += 6
            else:
                self.wr -= 6
        else:
            self.wr = self.desired_wr 
        

        self.velocity.x = (self.wl + self.wr) * self.wheel_radius / 2
        self.angular_velocity = (self.wr - self.wl) * self.wheel_radius / self.wheels_distance

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += math.degrees((self.angular_velocity) * dt)


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
        resized_image = pygame.transform.scale(car_image, (50, 50))
        car = Car(100, 360)
        ppu = 1

        while not self.exit:
            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            dt = self.clock.get_time() / 1000

            # Line sensor
            sensor_position_1 = car.position + Vector2(40, 10).rotate(-car.angle)
            sensor_position_2 = car.position + Vector2(40, -10).rotate(-car.angle)
            line_sensor_1 = self.screen.get_at((int(sensor_position_1.x), int(sensor_position_1.y)))
            line_sensor_2 = self.screen.get_at((int(sensor_position_2.x), int(sensor_position_2.y)))

            is_white_1 = (line_sensor_1[0] == 255)
            is_white_2 = (line_sensor_2[0] == 255)
            
            if is_white_1:
                car.desired_wl = 10
                car.desired_wr = 0
            elif is_white_2:
                car.desired_wl = 0
                car.desired_wr = 10
            else :
                car.desired_wl = 10
                car.desired_wr = 10

            car.update(dt)
            
            #Draw
            self.screen.fill((0, 0, 0))
            self.draw_map()

            line_sensor_draw_1 = sensor_position_1 + Vector2(10, 0).rotate(-car.angle)
            line_sensor_draw_2 = sensor_position_2 + Vector2(10, 0).rotate(-car.angle)
            pygame.draw.circle(self.screen, (255, 0, 255), (line_sensor_draw_1.x, line_sensor_draw_1.y), 4)
            pygame.draw.circle(self.screen, (255, 0, 255), (line_sensor_draw_2.x, line_sensor_draw_2.y), 4)

            rotated = pygame.transform.rotate(resized_image, car.angle)
            rect = rotated.get_rect()
            self.screen.blit(rotated, car.position * ppu - (rect.width / 2, rect.height / 2))
            pygame.display.flip()
            self.clock.tick(self.ticks)


            
        pygame.quit()

    def draw_map(self):
        map = Map(100, 500, 270, self.screen)

        map.gen_line(80)
        map.gen_marker('Right', map.last_point)
        map.gen_marker('Right', map.last_point + Vector2(100 , 0.0).rotate(map.last_angle))
        map.gen_line(260)


        map.gen_arc_right(30, 90)
        
        map.gen_line(420)

        map.gen_arc_right(100, 20)
        map.gen_arc_left(120, 40)
        map.gen_arc_right(100, 20)

        map.gen_line(420)

        map.gen_arc_right(80, 180)
        map.gen_arc_right(20, 90)
        map.gen_arc_left(80, 265)

        map.gen_line(100)

        map.gen_arc_right(50, 180)

        map.gen_line(600)

        map.gen_arc_left(20, 80)

        map.gen_line(115)

        map.gen_arc_left(80, 90)
        map.gen_arc_left(900, 40)
        map.gen_arc_left(20, 180)
        map.gen_arc_right(70, 50)
        map.gen_arc_left(70, 50)
        map.gen_arc_right(70, 50)
        map.gen_arc_left(70, 50)
        map.gen_arc_right(70, 50)
        map.gen_arc_left(70, 50)
        map.gen_arc_right(70, 50)
        map.gen_arc_left(70, 50)
        map.gen_arc_right(70, 125)

        map.gen_line(220)

        map.gen_arc_right(20, 180)
        map.gen_line(70)
        map.gen_arc_left(20, 180)
        map.gen_line(70)

        map.gen_arc_right(30, 100)
        map.gen_arc_left(60, 40)
        map.gen_arc_right(60, 90)
        map.gen_arc_right(20, 115)


        map.gen_line(400)

        map.gen_arc_left(100, 90)
        map.gen_arc_left(20, 90)
        map.gen_arc_right(50, 85)

        map.gen_line(170)

        map.gen_arc_right(80, 90)
        map.gen_arc_right(20, 200)
        map.gen_arc_left(20, 250)
        map.gen_arc_right(20, 125)

        map.gen_arc_left(20, 210)
        map.gen_arc_right(20, 210)
        map.gen_arc_left(20, 75)


        map.gen_line(25)

        map.gen_arc_right(20, 90)

        map.gen_line(105)

if __name__ == '__main__':
    game = Game()
    game.run()