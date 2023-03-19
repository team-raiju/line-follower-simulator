import math
from pygame.math import Vector2


class Robot:
    def __init__(self, x_cm, y_cm, angle):
        x = self.centimeters_to_pixel(x_cm)
        y = self.centimeters_to_pixel(y_cm)
        self.position = Vector2(x, y)
        self.wl = 0 #RPS
        self.wr = 0 #RPS
        self.angle = angle
        self.velocity = Vector2(1, 0.0)
        self.angular_velocity = 0
        self.wheels_distance = self.centimeters_to_pixel(18)
        self.wheel_radius = self.centimeters_to_pixel(2.5)
        self.desired_wl = 0
        self.desired_wr = 0
    
    def centimeters_to_pixel(self, centimeters):
        return centimeters * 2

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
        

        self.velocity.x = (self.wl + self.wr) * self.wheel_radius / 2 # Pixel per second
        self.angular_velocity = (self.wr - self.wl) * self.wheel_radius / self.wheels_distance # Pixel per second

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += math.degrees((self.angular_velocity) * dt)