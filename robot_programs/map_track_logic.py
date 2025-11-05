from .base_logic import RobotLogic
from helper import PIDFunctions as pid
from helper import CountMarkers as cm
from helper import Helper as hp
from pygame.math import Vector2
import math
import os

MIN_LEFT_MARKER_COUNTER = 40
TRACK_POINTS_DIST_CM = 5.0
MAPPING_NAME = "map6" 
SHORTCUT_MOVING_AVG_POINTS = 5  # Define the window size for the moving average

class MapTrackLogic(RobotLogic):
    """
    A logic that follows a line using PID and simultaneously
    maps the track by saving points and marker locations.
    """
    def __init__(self, **kwargs):
        base_speed = kwargs.get('base_speed', 60)
        kp = kwargs.get('kp', 35)
        kd = kwargs.get('kd', 50)

        self.pid_calc = pid(base_speed, kp, kd)
        self.count_markers = cm()

        self.left_marker_counter = 0
        self.right_marker_counter = 0
        
        self.time = 0.0
        self.finished = False
        self.last_error = 0.0

        self.last_dist_saved = 0
        self.last_theta = 0

        self.mapping_points = []
        self.shortcut_map = []
        self.radius_list = []
        
        print("MapTrackLogic initialized.")

    def get_time(self) -> float:
        return self.time

    def first_right_marker(self) -> bool:
        return self.right_marker_counter >= 1

    def process_tick(self, dt: float, line_sensor_data: list, robot_state: dict):
        # Timekeeping
        # print(robot_state['position_cm'])
        if not self.finished:
            self.time += dt
            self._append_point(robot_state['position_cm'], robot_state['angle_deg'], robot_state['total_dist_cm'])

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
            if self.right_marker_counter == 1 and self.left_marker_counter < 1:
                print("Start")
                self.time = 0.0
                self.last_dist_saved = 0
            elif self.left_marker_counter > MIN_LEFT_MARKER_COUNTER:
                if not self.finished:
                    print("Total time: " + str(round(self.time, 4)) + "s")
                    
                    print("Track mapping complete. Saving data...")
                    self._generate_shortcut_map()
                    self._save_mapping_data()
                    self.finished = True
                    self.pid_calc = pid(15, 3.5, 2)

        # Calculate Motor Output
        l_speed, r_speed = self.pid_calc.simple_pid(error)
        
        return l_speed, r_speed

    # --- Helper Methods ---
    
    def _append_point(self, robot_pos_cm, robot_angle, total_dist_cm):
        if (not self.first_right_marker()):
            return
        
        total_dist = float(total_dist_cm)
        if (total_dist > (self.last_dist_saved + TRACK_POINTS_DIST_CM)):
            radius = self.estimate_radius(robot_angle, self.last_theta, total_dist, self.last_dist_saved)
            
            self.radius_list.append(radius)
            self.mapping_points.append(robot_pos_cm.copy())
            print(f"Mapping point: {robot_pos_cm}, Radius: {radius}")

            self.last_dist_saved = total_dist
            self.last_theta = float(robot_angle)

    def _save_mapping_data(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one directory (from robot_logics) to find maps/
        base_dir = os.path.join(current_dir, "..") 
        file_path = os.path.join(base_dir, "maps", "mapping_data", MAPPING_NAME, (MAPPING_NAME + "_map_data.txt"))

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            for point in self.mapping_points:
                f.write(f"{point[0]},{point[1]}\n")

        file_path = os.path.join(base_dir, "maps", "mapping_data", MAPPING_NAME, (MAPPING_NAME + "_radius.txt"))
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            for radius in self.radius_list:
                f.write(f"{radius}\n")
        
        file_path = os.path.join(base_dir, "maps", "mapping_data", MAPPING_NAME, (MAPPING_NAME + "_shortcut_map.txt"))
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            for point in self.shortcut_map:
                f.write(f"{point[0]},{point[1]}\n")
        
    
    def estimate_radius(self, current_angle_deg, last_angle_deg, dist_traveled, previous_traveled_dist_cm):
        delta_theta_deg = hp.get_shortest_delta_angle(current_angle_deg, last_angle_deg)
        current_radius_cm = 100.0
        theta_rad = math.radians(delta_theta_deg)
        
        if abs(theta_rad) > 0.0175:
            current_radius_cm = (dist_traveled - previous_traveled_dist_cm) / theta_rad
        
        # limit radius cm to -100 to 100
        if current_radius_cm > 100:
            current_radius_cm = 100.0
        elif current_radius_cm < -100:
            current_radius_cm = -100.0

        return current_radius_cm
    
    def _generate_shortcut_map(self):
        """
        Generates a shortcut map by applying a moving average filter
        to the mapping points.
        """
        self.shortcut_map = []

        map_list_length = len(self.mapping_points)
        for i in range(map_list_length):
            half_window = SHORTCUT_MOVING_AVG_POINTS // 2

            if i < half_window:
                half_window = i
            elif i > map_list_length - half_window - 1:
                half_window = map_list_length - i - 1

            start_idx = max(0, i - half_window)
            end_idx = min(map_list_length, i + half_window + 1)

            sum_x = 0.0
            sum_y = 0.0

            for j in range(start_idx, end_idx):
                sum_x += self.mapping_points[j][0]
                sum_y += self.mapping_points[j][1]

            average_point = Vector2(sum_x / (end_idx - start_idx), sum_y / (end_idx - start_idx))
            self.shortcut_map.append(average_point)
