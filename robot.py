import math
from pygame.math import Vector2
from motor import Motor


class Robot:
    def __init__(self, x_cm, y_cm, angle):
        x = self.centimeters_to_pixel(x_cm)
        y = self.centimeters_to_pixel(y_cm)
        self.wheel_radius_cm = 1.5
        self.position = Vector2(x, y)
        self.angle = angle
        self.velocity = Vector2(1, 0.0)
        self.angular_velocity = 0
        self.wheels_distance = self.centimeters_to_pixel(18)

        self.motor_l = Motor(self.wheel_radius_cm)
        self.motor_r = Motor(self.wheel_radius_cm)
        self.motor_l.set_voltage(0)
        self.motor_r.set_voltage(0)

        self.mot_vel_l = 0.0
        self.mot_vel_r = 0.0
    
    def centimeters_to_pixel(self, centimeters):
        return centimeters * 2
    
    def meters_to_pixel(self, meters):
        return meters * 200

    def update(self, dt):
        self.mot_vel_l = self.motor_l.velocity_after_interval(self.mot_vel_l, dt) # m/s
        self.mot_vel_r = self.motor_r.velocity_after_interval(self.mot_vel_r, dt) # m/s
        
        self.velocity.x = self.meters_to_pixel((self.mot_vel_l + self.mot_vel_r) / 2)    # Pixel per second
        self.angular_velocity = self.meters_to_pixel((self.mot_vel_r - self.mot_vel_l)) / self.wheels_distance # Pixel per second / Pixel = rad/s

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += math.degrees((self.angular_velocity) * dt)