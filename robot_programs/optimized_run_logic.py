import os

from pygame import Vector2

from .base_logic import RobotLogic
from helper import PIDFunctions as pid
from helper import CountMarkers as cm
from helper import Helper as hp
import math

TRACK_POINTS_DIST_CM = 3.0
RADIUS_LIST = "../maps/mapping_data/map_example/map6_radius.txt"
MAP_LIST = "../maps/mapping_data/map_example/map6_map_data.txt"

class OptimizedRunLogic(RobotLogic):

    def __init__(self, **kwargs):
        self.target_speed = kwargs.get('base_speed', 40)

        self.kp = kwargs.get('kp', 35)
        self.kd = kwargs.get('kd', 50)
        ki = 0
        self.min_left_marker_counter = kwargs.get('min_left_marker_counter', 50)

        self.current_speed = 0
        self.pid_calc = pid(self.current_speed, self.kp, self.kd, ki)
        
        self.count_markers = cm()
        
        self.left_marker_counter = 0
        self.right_marker_counter = 0
        
        self.time = 0.0
        self.finished = False
        self.last_error = 0.0
        self.velocity_table = []
        self.last_update_dist = 0
        self.vel_idx = 0
        self.create_velocity_table_from_map()


    def get_time(self):
        return self.time
    
    def first_right_marker(self) -> bool:
        return self.right_marker_counter >= 1

    def process_tick(self, dt: float, line_sensor_data: list, robot_state: dict):
        # Timekeeping
        if not self.finished:
            self.time += dt

        # print(f"Current idx: {self.vel_idx}, Current Speed: {self.current_speed}, Target Speed: {self.target_speed}")
        if self.current_speed < self.target_speed:
            self.current_speed += 5
            self.pid_calc.set_base_speed(self.current_speed)

        if self.current_speed > self.target_speed:
            self.current_speed -= 10
            self.pid_calc.set_base_speed(self.current_speed)

        if self.first_right_marker():
            total_dist = float(robot_state['total_dist_cm'])
            if total_dist > (self.last_update_dist + TRACK_POINTS_DIST_CM):
                self.vel_idx += 1
                if (self.vel_idx >= len(self.velocity_table)):
                    self.vel_idx = len(self.velocity_table) - 1
                new_vel = self.velocity_table[self.vel_idx]
                print(f"Updating velocity to: {new_vel} at distance {total_dist} cm")

                self.target_speed = new_vel
                self.last_update_dist = total_dist

        # Process Sensors
        filtered_line_sensor = hp.filter_line(line_sensor_data, robot_state['white_val'], robot_state['black_val'])

        # Calculate Error for PID
        error = pid.calc_error(filtered_line_sensor, robot_state['line_sensor_positions'])
        if error == -99:
            error = self.last_error
        else:
            self.last_error = error

        # Process Markers
        markers = self.count_markers.marker_process(
            filtered_line_sensor[16:18], filtered_line_sensor[18:20],
            robot_state['white_val'], robot_state['position_cm'], robot_state['angle_deg']
        )

        if markers["left_marker"]["seeing"]:
            self.left_marker_counter += 1
            print("Left marker - " + str(self.left_marker_counter))

        if markers["right_marker"]["seeing"]:
            self.right_marker_counter += 1
            print("Right marker - " + str(self.right_marker_counter))
            if self.right_marker_counter == 1 and self.left_marker_counter < 1:
                print("Start")
                self.time = 0.0
            elif self.left_marker_counter > self.min_left_marker_counter:
                if not self.finished:
                    print("Total time: " + str(round(self.time, 4)) + "s")
                    self.finished = True
                    self.pid_calc = pid(15, 3.5, 2)

        # Calculate Motor Output
        l_speed, r_speed = self.pid_calc.simple_pid(error)
        if (self.finished):
            l_speed = 0
            r_speed = 0

        return l_speed, r_speed

    def create_velocity_table(self):

        radius_list = []
        current_dir = os.path.dirname(os.path.abspath(__file__))

        file_name = RADIUS_LIST

        radius_list_path = os.path.join(current_dir, file_name)

        with open(radius_list_path, "r") as f:
            for line in f:
                radius_val = float(line.strip())
                radius_list.append(abs(radius_val))

        for radius in radius_list:
            velocity = self.radius_to_velocity(radius)
            self.velocity_table.append(velocity)

        self.filter_velocity_table()
        self.add_break_before_turn(5)
    
    def create_velocity_table_from_map(self):
        map_list = []
        current_dir = os.path.dirname(os.path.abspath(__file__))

        map_list_path = os.path.join(current_dir, MAP_LIST)

        try:
            with open(map_list_path, "r") as f:
                for line in f:
                    x_cm, y_cm = line.strip().split(",")
                    point = Vector2(float(x_cm), float(y_cm))
                    map_list.append(point)
        except FileNotFoundError:
             print(f"FATAL: Waypoint file not found at {map_list_path}")
             return []
        except Exception as e:
            print(f"Error loading waypoint file: {e}")
            return []
        
        profile_length = len(map_list)

        points_ahead = int(8 / TRACK_POINTS_DIST_CM)

        track_current_theta = 0.0
        track_last_theta = 0.0

        self.velocity_table = [self.radius_to_velocity(40)] * profile_length

        for i in range(0, profile_length - points_ahead, points_ahead):

            p1 = map_list[i]
            p2 = map_list[i + points_ahead]

            track_current_theta -= hp.angle_to_point_rad(p1, p2, track_current_theta)
            delta_theta = hp.get_shortest_delta_angle_rad(track_current_theta, track_last_theta)

            estimated_radius_cm = 100
            if (delta_theta != 0):
                estimated_radius_cm = (points_ahead * TRACK_POINTS_DIST_CM) / delta_theta

            
            if estimated_radius_cm > 100.0:
                estimated_radius_cm = 100.0
            elif estimated_radius_cm < -100.0:
                estimated_radius_cm = -100.0
            
            radius_cm_abs = abs(estimated_radius_cm)

            velocity = self.radius_to_velocity(radius_cm_abs)
            for j in range(points_ahead):
                if (i + j) < profile_length:
                    self.velocity_table[i + j] = velocity

            track_last_theta = track_current_theta

        # Fill in the last few points with the last calculated velocity
        last_calculated_index = max(0, profile_length - points_ahead - 1)
        last_velocity = self.velocity_table[last_calculated_index]
        for i in range(profile_length - points_ahead, profile_length):
            self.velocity_table[i] = last_velocity


        # print(self.velocity_table)
        self.filter_velocity_table()
        self.add_break_before_turn(7)
    
    def filter_velocity_table(self):
        for i in range(1, len(self.velocity_table) - 1):
            previous_velocity = self.velocity_table[i - 1]
            current_velocity = self.velocity_table[i]
            next_velocity = self.velocity_table[i + 1]

            if (previous_velocity == next_velocity) and (current_velocity != previous_velocity):
                self.velocity_table[i] = previous_velocity
        
        
        for i in range(1, len(self.velocity_table) - 2):
            previous_velocity = self.velocity_table[i - 1]
            current_velocity = self.velocity_table[i]
            next_next_velocity = self.velocity_table[i + 2]

            if (previous_velocity == 100) and (current_velocity != 100) and (next_next_velocity == 100):
                self.velocity_table[i] = 100

    def add_break_after_turn(self, break_size: int):
        if break_size == 0:
            return

        for i in range(len(self.velocity_table) - 3, 0, -1):
            v_diff_1 = self.velocity_table[i] - self.velocity_table[i + 1]
            v_diff_2 = self.velocity_table[i] - self.velocity_table[i + 2]

            if (v_diff_1 < 0) and (v_diff_2 < 0):
                for j in range(break_size):
                    target_index = i + j + 2
                    if target_index >= len(self.velocity_table):
                        break

                    if self.velocity_table[target_index] > self.velocity_table[i]:
                        self.velocity_table[target_index] = self.velocity_table[i]

    def add_break_before_turn(self, break_size: int):
        if break_size == 0:
            return

        for i in range(len(self.velocity_table) - 2):
            v_diff_1 = self.velocity_table[i + 1] - self.velocity_table[i]
            v_diff_2 = self.velocity_table[i + 2] - self.velocity_table[i]

            # Find if we are braking and apply "break_size" steps before
            if (v_diff_1 < 0) and (v_diff_2 < 0):
                for j in range(break_size):
                    if (i - j) < 0:
                        break

                    # Only change velocity if it was greater
                    if self.velocity_table[i - j] > self.velocity_table[i + 1]:
                        self.velocity_table[i - j] = self.velocity_table[i + 1]

    def radius_to_velocity(self, radius):
        velocity = 50
        if(radius < 20):
            velocity = 50
        elif(radius < 30):
            velocity = 50
        elif(radius < 50):
            velocity = 50
        elif(radius < 70):
            velocity = 60
        else:
            velocity = 100
        
        return velocity