import math
from pygame.surface import Surface
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

        # Line sensor position in centimeters from robot center
        self.line_sensor_pos = [
            Vector2(20, -4),
            Vector2(20, -3),
            Vector2(20, -1),
            Vector2(20,  1),
            Vector2(20,  3),
            Vector2(20,  4),
        ]
    
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
    
    def get_line_sensor(self, screen: Surface, max_x, max_y):
        
        sensor_val = []

        for pos_vector in self.line_sensor_pos:
            sensor_position = self.position + self.centimeters_to_pixel(pos_vector).rotate(-self.angle)

            if (int(sensor_position.x) <= 0 or int(sensor_position.x) >= max_x):
                sensor_val.append(1)
            elif (int(sensor_position.y) <= 0 or int(sensor_position.y) >= max_y):
                sensor_val.append(1)
            
            else:
                val = screen.get_at((int(sensor_position.x), int(sensor_position.y)))
                
                is_black = (val[0] != 255)
                if is_black:
                    sensor_val.append(1)
                else:
                    sensor_val.append(0)


        return sensor_val
    
    def out_of_line(self, screen: Surface, max_x, max_y):
        corners = [Vector2(0, 0), Vector2(0, 0), Vector2(0, 0), Vector2(0, 0)]
        robot_size_x_pixel = self.wheels_distance + 10
        robot_size_y_pixel = self.wheels_distance + 10
        corners[0] = self.position + (Vector2(robot_size_x_pixel / 2, robot_size_y_pixel / 2)).rotate(-self.angle)
        corners[1] = self.position + (Vector2(robot_size_x_pixel / 2, -robot_size_y_pixel / 2)).rotate(-self.angle)
        corners[2] = self.position + (Vector2(-robot_size_x_pixel / 2, -robot_size_y_pixel / 2)).rotate(-self.angle)
        corners[3] = self.position + (Vector2(-robot_size_x_pixel / 2, robot_size_y_pixel / 2)).rotate(-self.angle)

        # Check if out of screen
        for corner in corners:
            if (int(corner.x) <= 0 or int(corner.x) >= max_x):
                return True
            if (int(corner.y) <= 0 or int(corner.y) >= max_y):
                return True

        # Check if white line cross any of the borders
        for i in range (0, int(robot_size_x_pixel), 2):
            point = corners[0] + Vector2(i, 0).rotate(-self.angle-90)
            color = screen.get_at((int(point.x), int(point.y)))
            if (color[0] == 255):
                return False

        for i in range (0, int(robot_size_y_pixel), 2):
            point = corners[1] + Vector2(i, 0).rotate(-self.angle-180)
            color = screen.get_at((int(point.x), int(point.y)))
            if (color[0] == 255):
                return False
        
        for i in range (0, int(robot_size_x_pixel), 2):
            point = corners[2] + Vector2(i, 0).rotate(-self.angle-270)
            color = screen.get_at((int(point.x), int(point.y)))
            if (color[0] == 255):
                return False
        
        for i in range (0, int(robot_size_y_pixel), 2):
            point = corners[3] + Vector2(i, 0).rotate(-self.angle)
            color = screen.get_at((int(point.x), int(point.y)))
            if (color[0] == 255):
                return False
        
        return True