import math
import pygame
from pygame.surface import Surface
from pygame.math import Vector2
from motor import Motor
import os

LINE_COLOR_THRESHOLD = 150
ENCODER_PPR = 7

BLACK_VAL = 0
WHITE_VAL = 1

class Robot:
    def __init__(self, cm_per_pixel, size_x_cm, size_y_cm, rot_center_offset_cm, wheels_dist_cm, wheel_radius_cm, pos_x_cm, pos_y_cm, angle, image):
        #Robot position
        self.cm_per_pixel = cm_per_pixel
        x = self.centimeters_to_pixel(pos_x_cm)
        y = self.centimeters_to_pixel(pos_y_cm)
        self.position = Vector2(x, y)
        self.angle = angle
        self.estimated_position_cm = Vector2(pos_x_cm, pos_y_cm)
        self.estimated_angle = angle

        
        # Robot Params
        self.wheel_radius_cm = wheel_radius_cm
        self.wheels_distance_cm = wheels_dist_cm
        self.robot_size_x_cm = size_x_cm
        self.robot_size_y_cm = size_y_cm
        self.rot_center_offset_cm = rot_center_offset_cm
        
        # Line sensor position in centimeters from robot center
        self.white_val = WHITE_VAL
        self.black_val = BLACK_VAL
        self.line_sensor_pos = [
            Vector2(6.76, -4.0),
            Vector2(6.76, -3.50),
            Vector2(6.76, -3.00),
            Vector2(6.76, -2.50),
            Vector2(6.76, -2.00),
            Vector2(6.76, -1.50),
            Vector2(6.76, -1.00),
            Vector2(6.76, -0.50),

            Vector2(6.76, 0.50),
            Vector2(6.76, 1.0),
            Vector2(6.76, 1.5),
            Vector2(6.76, 2.0),
            Vector2(6.76, 2.5),
            Vector2(6.76, 3.0),
            Vector2(6.76, 3.5),
            Vector2(6.76, 4),


            Vector2(-0.1,  -8),
            Vector2(-0.1,  -6.5),
            
            Vector2(-0.1,  8),
            Vector2(-0.1,  6.5),


        ]

        self.wheel_perimeter_cm = 2 * math.pi * self.wheel_radius_cm
        self.dist_per_encoder_pulse_cm = self.wheel_perimeter_cm / ENCODER_PPR

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

        self.left_encoder = 0
        self.right_encoder = 0
        self.left_encoder_last = 0
        self.right_encoder_last = 0
        self.left_encoder_raw = 0
        self.right_encoder_raw = 0
        self.estimated_total_dist_cm = 0
        self.total_dist_cm = 0

    
    def centimeters_to_pixel(self, centimeters):
        return centimeters * self.cm_per_pixel 
    
    def meters_to_pixel(self, meters):
        return meters * self.cm_per_pixel  * 100
    
    def update_estimated_pos(self, mot_vel_l, mot_vel_r, dt):
        # simulate encoder values
        num_of_rot_l = ((mot_vel_l * 100) * dt) / self.dist_per_encoder_pulse_cm
        num_of_rot_r = ((mot_vel_r * 100) * dt) / self.dist_per_encoder_pulse_cm
        self.left_encoder_raw += num_of_rot_l
        self.right_encoder_raw += num_of_rot_r
        self.left_encoder = math.floor(self.left_encoder_raw)
        self.right_encoder = math.floor(self.right_encoder_raw)

        # print(str(self.left_encoder_raw * self.dist_per_encoder_pulse_cm) + ", " + str(self.left_encoder * self.dist_per_encoder_pulse_cm))

        #estimate velocity based on encoder value
        estimated_delta_l_cm = 0
        estimated_delta_r_cm = 0
        changed = False
        if (self.left_encoder_last != self.left_encoder):
            estimated_delta_l_cm = ((self.left_encoder - self.left_encoder_last) * self.dist_per_encoder_pulse_cm)
            self.left_encoder_last = int(self.left_encoder)
            changed = True

        if (self.right_encoder_last != self.right_encoder):
            estimated_delta_r_cm = ((self.right_encoder - self.right_encoder_last) * self.dist_per_encoder_pulse_cm)
            self.right_encoder_last = int(self.right_encoder)
            changed = True

        if (changed):
            estimated_delta = Vector2(1, 0.0)
            estimated_delta.x = (estimated_delta_l_cm + estimated_delta_r_cm) / 2
            estimated_delta_angle = (estimated_delta_r_cm - estimated_delta_l_cm) / self.wheels_distance_cm

            self.estimated_total_dist_cm += estimated_delta.x
            self.estimated_position_cm += estimated_delta.rotate(-self.estimated_angle)
            self.estimated_angle += math.degrees((estimated_delta_angle))



    def update(self, dt):
        self.mot_vel_l = self.motor_l.velocity_after_interval(self.mot_vel_l, dt) # m/s
        self.mot_vel_r = self.motor_r.velocity_after_interval(self.mot_vel_r, dt) # m/s

        self.update_estimated_pos(self.mot_vel_l, self.mot_vel_r, dt)
        
        self.velocity.x = self.meters_to_pixel((self.mot_vel_l + self.mot_vel_r) / 2)    # Pixel per second

        self.angular_velocity = self.meters_to_pixel((self.mot_vel_r - self.mot_vel_l)) / self.wheels_distance_pixels # Pixel per second / Pixel = rad/s

        self.total_dist_cm += (self.velocity.x * dt) / self.cm_per_pixel
        
        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += math.degrees((self.angular_velocity) * dt)
    
    def get_line_sensor(self, screen: Surface, max_x, max_y):
        
        sensor_val = []

        for pos_vector in self.line_sensor_pos:
            offset = Vector2(self.centimeters_to_pixel(self.rot_center_offset_cm), 0)
            sensor_position = self.position + self.centimeters_to_pixel(pos_vector).rotate(-self.angle) + offset.rotate(-self.angle)

            if (int(sensor_position.x) <= 0 or int(sensor_position.x) >= max_x):
                sensor_val.append(self.black_val)
            elif (int(sensor_position.y) <= 0 or int(sensor_position.y) >= max_y):
                sensor_val.append(self.black_val)
            
            else:
                val = screen.get_at((int(sensor_position.x), int(sensor_position.y)))
                is_black = (val[0] < LINE_COLOR_THRESHOLD)
                if is_black:
                    sensor_val.append(self.black_val)
                else:
                    sensor_val.append(self.white_val)


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
    
    def display_rot_center(self, screen: Surface):
        pygame.draw.circle(screen, (255, 255, 255), (self.position.x, self.position.y), 2)
    
    # Voltage is proportional to a linear and angular velocity, but is not in a standard unit (such as m/s or rad/s)
    def set_motors_voltage_vel_w(self, vel, w):
        self.motor_l.set_voltage((2 * vel - (w * self.wheels_distance_cm)) / 2)
        self.motor_r.set_voltage((2 * vel + (w * self.wheels_distance_cm)) / 2) 
    
    def set_motors_voltage(self, l_speed, r_speed):
        self.motor_l.set_voltage(l_speed)
        self.motor_r.set_voltage(r_speed)