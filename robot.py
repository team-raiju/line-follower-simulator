import math
import pygame
from pygame.surface import Surface
from pygame.math import Vector2
from motor import Motor
import os

LINE_COLOR_THRESHOLD = 150

class Robot:
    def __init__(self, cm_per_pixel, size_x_cm, size_y_cm, rot_center_offset_cm, wheels_dist_cm, wheel_radius_cm, pos_x_cm, pos_y_cm, angle, image):
        #Robot position
        self.cm_per_pixel = cm_per_pixel
        x = self.centimeters_to_pixel(pos_x_cm)
        y = self.centimeters_to_pixel(pos_y_cm)
        self.position = Vector2(x, y)
        self.angle = angle
        
        # Robot Params
        self.wheel_radius_cm = wheel_radius_cm
        self.wheels_distance_cm = wheels_dist_cm
        self.robot_size_x_cm = size_x_cm
        self.robot_size_y_cm = size_y_cm
        self.rot_center_offset_cm = rot_center_offset_cm
        
        # Line sensor position in centimeters from robot center
        self.line_sensor_pos = [
            Vector2(4.22, -4.56),
            Vector2(4.62, -3.98),
            Vector2(5.10, -3.4),
            Vector2(5.44, -2.82),
            Vector2(5.84, -2.24),
            Vector2(6.18, -1.66),
            Vector2(6.38, -1.08),
            Vector2(6.66, -0.50),

            Vector2(6.66, 0.50),
            Vector2(6.38, 1.08),
            Vector2(6.18, 1.66),
            Vector2(5.84, 2.24),
            Vector2(5.44, 2.82),
            Vector2(5.10, 3.4),
            Vector2(4.62, 3.98),
            Vector2(4.22, 4.56),


            Vector2(-0.3,  -7.2),
            Vector2(-0.6,  -6.5),
            
            Vector2(-0.3,  7.2),
            Vector2(-0.6,  6.5),


        ]

        self.wheels_distance_pixels = self.centimeters_to_pixel(self.wheels_distance_cm)

        self.motor_l = Motor(self.wheel_radius_cm)
        self.motor_r = Motor(self.wheel_radius_cm)
        self.motor_l.set_voltage(0)
        self.motor_r.set_voltage(0)

        self.mot_vel_l = 0.0
        self.mot_vel_r = 0.0

        self.velocity = Vector2(1, 0.0)
        self.angular_velocity = 0

        current_dir = os.path.dirname(os.path.abspath(__file__))
        robot_image_path = os.path.join(current_dir, "media" , image)
        robot_image = pygame.image.load(robot_image_path)

        self.resized_robot_img = pygame.transform.scale(robot_image, (self.centimeters_to_pixel(self.robot_size_y_cm), self.centimeters_to_pixel(self.robot_size_x_cm)))

    
    def centimeters_to_pixel(self, centimeters):
        return centimeters * self.cm_per_pixel 
    
    def meters_to_pixel(self, meters):
        return meters * self.cm_per_pixel  * 100

    def update(self, dt):
        self.mot_vel_l = self.motor_l.velocity_after_interval(self.mot_vel_l, dt) # m/s
        self.mot_vel_r = self.motor_r.velocity_after_interval(self.mot_vel_r, dt) # m/s
        
        self.velocity.x = self.meters_to_pixel((self.mot_vel_l + self.mot_vel_r) / 2)    # Pixel per second

        self.angular_velocity = self.meters_to_pixel((self.mot_vel_r - self.mot_vel_l)) / self.wheels_distance_pixels # Pixel per second / Pixel = rad/s

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += math.degrees((self.angular_velocity) * dt)
    
    def get_line_sensor(self, screen: Surface, max_x, max_y):
        
        sensor_val = []

        for pos_vector in self.line_sensor_pos:
            offset = Vector2(self.centimeters_to_pixel(self.rot_center_offset_cm), 0)
            sensor_position = self.position + self.centimeters_to_pixel(pos_vector).rotate(-self.angle) + offset.rotate(-self.angle)

            if (int(sensor_position.x) <= 0 or int(sensor_position.x) >= max_x):
                sensor_val.append(1)
            elif (int(sensor_position.y) <= 0 or int(sensor_position.y) >= max_y):
                sensor_val.append(1)
            
            else:
                val = screen.get_at((int(sensor_position.x), int(sensor_position.y)))
                is_black = (val[0] < LINE_COLOR_THRESHOLD)
                if is_black:
                    sensor_val.append(1)
                else:
                    sensor_val.append(0)


        return sensor_val
    
    def out_of_line(self, screen: Surface, max_x, max_y):
        corners = [Vector2(0, 0), Vector2(0, 0), Vector2(0, 0), Vector2(0, 0)]

        margin = 10
        robot_size_x_pixel = self.centimeters_to_pixel(self.robot_size_x_cm) + margin
        robot_size_y_pixel = self.centimeters_to_pixel(self.robot_size_y_cm) + margin

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
            if (color[0] > LINE_COLOR_THRESHOLD):
                return False

        for i in range (0, int(robot_size_y_pixel), 2):
            point = corners[1] + Vector2(i, 0).rotate(-self.angle-180)
            color = screen.get_at((int(point.x), int(point.y)))
            if (color[0] > LINE_COLOR_THRESHOLD):
                return False
        
        for i in range (0, int(robot_size_x_pixel), 2):
            point = corners[2] + Vector2(i, 0).rotate(-self.angle-270)
            color = screen.get_at((int(point.x), int(point.y)))
            if (color[0] > LINE_COLOR_THRESHOLD):
                return False
        
        for i in range (0, int(robot_size_y_pixel), 2):
            point = corners[3] + Vector2(i, 0).rotate(-self.angle)
            color = screen.get_at((int(point.x), int(point.y)))
            if (color[0] > LINE_COLOR_THRESHOLD):
                return False
        
        return True

    def rotate_image(self, angle, pivot, offset):
        rotated_image = pygame.transform.rotozoom(self.resized_robot_img, -angle, 1)  
        rotated_offset = offset.rotate(angle)  
        rect = rotated_image.get_rect(center = pivot + rotated_offset)
        return rotated_image, rect 

    def display(self, screen: Surface):
        robot_center = self.position
        offset = Vector2(self.centimeters_to_pixel(self.rot_center_offset_cm), 0)
        rotated_image, rect = self.rotate_image(-self.angle, robot_center, offset)
        screen.blit(rotated_image, rect)  # Blit the rotated image.
        # pygame.draw.circle(screen, (30, 250, 70), robot_center, 3)  # Pivot point.
        # pygame.draw.rect(screen, (30, 250, 70), rect, 1)  # The rect.
    
    def display_line_sensor(self, screen: Surface):
        for sensor in self.line_sensor_pos:
                offset = Vector2(self.centimeters_to_pixel(self.rot_center_offset_cm), 0)
                sensor_position = self.position + self.centimeters_to_pixel(sensor).rotate(-self.angle) + offset.rotate(-self.angle)
                line_sensor_draw = sensor_position
                pygame.draw.circle(screen, (255, 0, 255), (line_sensor_draw.x, line_sensor_draw.y), 2)