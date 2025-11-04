import pygame
from pygame.math import Vector2


class Helper:
    
    def filter_line(line_sensor: list, white_val, black_val):
        # If lateral sensors seeing
        if (line_sensor[0] == white_val or line_sensor[1] == white_val
                or line_sensor[14] == white_val or line_sensor[15] == white_val):
            
            # if Middle sensors seeing
            if (line_sensor[7] == white_val or line_sensor[8] == white_val
                    or line_sensor[6] == white_val or line_sensor[9] == white_val):
                
                # Clear letaral sensors
                line_sensor[0] = black_val
                line_sensor[1] = black_val
                line_sensor[15] = black_val
                line_sensor[14] = black_val
        return line_sensor
    
    def draw_timer(screen, time, cm_per_pixel):
        text_surface = pygame.font.Font(None, int(13 * cm_per_pixel)).render(
            "Time: " + "{:.3f}s".format(time), True, (255, 0, 0)
        )
        screen.blit(text_surface, (5, 5))
    
    def coord_cm_to_pixel(point, map_cm_to_pixel, map_margin_cm):
        x_val_pixel = (point[0] + map_margin_cm) * map_cm_to_pixel
        y_val_pixel = (point[1] + map_margin_cm) * map_cm_to_pixel
        return x_val_pixel, y_val_pixel

    def coord_pixel_to_cm(pixel, map_cm_to_pixel, map_margin_cm):
        x_val_cm = (pixel[0] / map_cm_to_pixel) - map_margin_cm
        y_val_cm, = (pixel[1] / map_cm_to_pixel) - map_margin_cm
        return x_val_cm, y_val_cm
    
    def get_shortest_delta_angle(a, b):
        delta = a - b
        if delta > 180:
            delta -= 360
        elif delta < -180:
            delta += 360
        return delta

class CountMarkers:
    def __init__(self):
        self.maybe_left_marker = False
        self.maybe_right_marker = False
        self.left_marker_position_raw = Vector2(0, 0)
        self.right_marker_position_raw = Vector2(0, 0)
        self.left_marker_angle_raw = 0
        self.right_marker_angle_raw = 0
        self.last_left_marker = False
        self.last_right_marker = False
    
    def marker_process(self, left_marker_sensors: list, right_marker_sensors: list, white_val, robot_pos: Vector2, robot_angle):
        
        tmp_left_marker = False
        tmp_right_marker = False

        return_dict = {
            "left_marker" : {
                "seeing": False, 
                "position": Vector2(0,0),
                "rotation": 0
            },
            "right_marker" : {
                "seeing": False, 
                "position": Vector2(0,0),
                "rotation": 0,
            }
        }

        for sensor in left_marker_sensors:
            if (sensor == white_val):
                tmp_left_marker = True
        
        for sensor in right_marker_sensors:
            if (sensor == white_val):
                tmp_right_marker = True
        
        # Process left markers. Check for crossing line
        if (self.maybe_left_marker):
                if (tmp_right_marker):
                    self.maybe_left_marker = False
                    print("Crossing L")
                elif (not tmp_left_marker and self.last_left_marker):
                    return_dict["left_marker"]["seeing"] = True
                    return_dict["left_marker"]["position"] = self.left_marker_position_raw
                    return_dict["left_marker"]["rotation"] = self.left_marker_angle_raw
                    self.maybe_left_marker = False

        else:
            if (tmp_left_marker and not self.last_left_marker and not tmp_right_marker):
                self.maybe_left_marker = True

                self.left_marker_position_raw = Vector2(robot_pos.x, robot_pos.y)
                self.left_marker_angle_raw = robot_angle
        

        # Process right markers. Check for crossing line
        if (self.maybe_right_marker):
                if (tmp_left_marker):
                    self.maybe_right_marker = False
                    print("Crossing R")
                elif (not tmp_right_marker and self.last_right_marker):
                    return_dict["right_marker"]["seeing"] = True
                    return_dict["right_marker"]["position"] = self.right_marker_position_raw
                    return_dict["right_marker"]["rotation"] = self.right_marker_angle_raw
                    self.maybe_right_marker = False

        else:
            if (tmp_right_marker and not self.last_right_marker and not tmp_left_marker):
                self.maybe_right_marker = True

                self.right_marker_position_raw = Vector2(robot_pos.x, robot_pos.y)
                self.right_marker_angle_raw = robot_angle


        self.last_left_marker = tmp_left_marker
        self.last_right_marker = tmp_right_marker
        
        return return_dict

class PIDFunctions:

    def __init__(self, speed, kp, kd, ki=0):
        self.kp = kp
        self.kd = kd
        self.ki = ki
        self.base_speed = speed
        self.last_error = 0
        self.integral = 0
    
    def set_kp(self, new_kp):
        self.kp = new_kp

    def set_kd(self, new_kd):
        self.kd = new_kd

    def set_ki(self, new_ki):
        self.ki = new_ki
    
    def set_base_speed(self, new_speed):
        self.base_speed = new_speed
    
    def get_last_error(self):
        return self.last_error
        
    def calc_error(line_sensor_val: list, central_sensors_pos_list: list):
        # Similar to center of mass calculation
        num_half_sensors = int(len(central_sensors_pos_list) / 2)

        # Weight list is based on the distance to center of each line sensor
        weight_list = []
        for idx in range(num_half_sensors):
            weight_list.append(central_sensors_pos_list[num_half_sensors + idx].y)

        count_left = 0
        count_right = 0
        sum_left = 0
        sum_right = 0
        for i in range(num_half_sensors):
            count_left += line_sensor_val[i]
            count_right += line_sensor_val[num_half_sensors + i]

            sum_left += weight_list[i] * line_sensor_val[num_half_sensors - 1 - i]
            sum_right += weight_list[i] * line_sensor_val[num_half_sensors + i]

        if count_left == 0 and count_right == 0:
            return -99
        if count_left == 0:
            count_left = 1
        if count_right == 0:
            count_right = 1
        pos_left = sum_left / count_left
        pos_right = sum_right / count_right

        return pos_left - pos_right
    
    def simple_pid(self, error):
        derivative = error - self.last_error
        l_speed = self.base_speed - (error * self.kp + derivative * self.kd)
        r_speed = self.base_speed + (error * self.kp + derivative * self.kd)
        self.last_error = error

        return l_speed, r_speed
    
    def pid_process(self, error):
        derivative = error - self.last_error
        self.integral += error
        result = (error * self.kp + derivative * self.kd + self.integral * self.ki)

        self.last_error = error

        return result
    
    def angle_pid(self, error):
        derivative = (error - self.last_error)
        w = (error * self.kp + derivative * self.kd)

        self.last_error = error
        return w