import os
import math
from pygame.math import Vector2
from .base_logic import RobotLogic
from helper import PIDFunctions as pid
from helper import CountMarkers as cm
from helper import Helper as hp

MAP_FILE = "../maps/mapping_data/map6/map6_map_data.txt"

class PurePursuitLogic(RobotLogic):
    """
    A robot logic that follows a list of waypoints using the
    Pure Pursuit path tracking algorithm.
    """
    
    def __init__(self, **kwargs):
        # Load parameters from kwargs
        self.base_speed = kwargs.get('base_speed', 50)
        self.wheels_dist_cm = kwargs.get('wheels_dist_cm', 12.0)
        self.look_ahead = kwargs.get('look_ahead', 10)
        self.max_waypoints_ahead = kwargs.get('max_waypoints_ahead', 8)
        self.map_cm_per_pixel = kwargs.get('map_cm_per_pixel', 3)

        # Internal state
        self.time = 0.0
        self.finished = False
        self.waypoint_idx = 0
        self.w_pid_calc = pid(0, 1, 2, 0.0) # PID for angular velocity
        self.pid_calc = pid(40, 25, 40)

        self.count_markers = cm()
        self.left_marker_counter = 0
        self.right_marker_counter = 0
        
        # Load waypoints
        self.waypoint_list = self._load_waypoint_list(MAP_FILE)
        if not self.waypoint_list:
            print("FATAL: PurePursuitLogic failed to load waypoints. Logic will not run.")
            self.finished = True
        else:
            print(f"PurePursuitLogic initialized. Loaded {len(self.waypoint_list)} waypoints.")

    def get_time(self) -> float:
        return self.time

    def first_right_marker(self) -> bool:
        return self.right_marker_counter >= 1

    def process_pid(self, line_sensor_data, robot_state):
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

        # Calculate Motor Output
        l_speed, r_speed = self.pid_calc.simple_pid(error)
        
        return l_speed, r_speed

    def process_tick(self, dt: float, line_sensor_data: list, robot_state: dict):
        if not self.finished:
            self.time += dt
        
        if not self.first_right_marker():
            return self.process_pid(line_sensor_data, robot_state)
        
        # --- 1. Get current state ---
        # Pure pursuit logic works in PIXELS, so we must convert state
        pos_cm = robot_state['position_cm']
        robot_angle = robot_state['angle_deg']
        angular_velocity = robot_state['angular_velocity']
        

        # --- 2. Main Logic: Follow Waypoints ---
        if self.waypoint_idx < len(self.waypoint_list) - 1:
            (dist, angleDiff) = self._trackGoal(pos_cm, self.waypoint_list[self.waypoint_idx], robot_angle)
            
            # Calculate curvature (R)
            R = 10000.0 # Default to straight line
            if(abs(angleDiff) > 1):
                R = self.look_ahead / (2 * math.sin(math.radians(angleDiff)))
            
            # Calculate motor speeds
            base_rot_ratio = (self.wheels_dist_cm / (2 * R)) * self.base_speed
            target_w = (2 * base_rot_ratio) / (self.wheels_dist_cm * 0.01) # rad/s
            error_w = target_w - angular_velocity

            w_pid = self.w_pid_calc.pid_process(error_w)
            alpha = ((self.wheels_dist_cm * 0.01) * w_pid) / 2

            l_speed = self.base_speed + base_rot_ratio + alpha
            r_speed = self.base_speed - base_rot_ratio - alpha

            # --- 3. Update Target Waypoint ---
            # Find the next best waypoint to track based on look-ahead distance
            front_vector = Vector2(11, 0) # A point x cm in front of the robot
            point_front = pos_cm + front_vector.rotate(-robot_angle)

            min_diff_modulo = 1000
            look_ahead_point_idx = self.waypoint_idx
            
            for i in range(self.max_waypoints_ahead):
                current_idx = self.waypoint_idx + i
                if current_idx >= len(self.waypoint_list):
                    look_ahead_point_idx = len(self.waypoint_list) - 1
                    break
                
                diff = point_front.distance_to(self.waypoint_list[current_idx]) - self.look_ahead
                
                if (diff < 0 and abs(diff) < min_diff_modulo):
                    min_diff_modulo = abs(diff)
                    look_ahead_point_idx = current_idx
            
            self.waypoint_idx = look_ahead_point_idx

            return l_speed, r_speed

        # --- 4. Finished Logic ---
        else:
            if not self.finished:
                print("Total time: " + str(round(self.time, 4)) + "s")
                self.finished = True
            return 0.0, 0.0 # Stop

    # --- Helper Methods ---

    def _load_waypoint_list(self, waypoints_file_name: str) -> list:
        """Loads waypoints from a file and converts them to pixel coordinates."""
        waypoint_list = []
        current_dir = os.path.dirname(os.path.abspath(__file__))

        waypoint_list_path = os.path.join(current_dir, waypoints_file_name)

        try:
            with open(waypoint_list_path, "r") as f:
                for line in f:
                    x_cm, y_cm = line.strip().split(",")
                    point = Vector2(float(x_cm), float(y_cm))
                    waypoint_list.append(point)
        except FileNotFoundError:
             print(f"FATAL: Waypoint file not found at {waypoint_list_path}")
             return []
        except Exception as e:
            print(f"Error loading waypoint file: {e}")
            return []
        
        return waypoint_list

    def _trackGoal(self, currentPos: Vector2, goal: Vector2, robot_angle: float) -> tuple:
        """Calculates the distance and angle difference to a goal point."""
        dist = currentPos.distance_to(goal)

        dx = goal.x - currentPos.x
        dy = goal.y - currentPos.y

        # Angle to the goal in degrees
        angleDiffRaw = (math.atan2(dy, dx) * 180 / math.pi)

        # Difference between robot's angle and angle to goal
        angleDiff = angleDiffRaw - (-robot_angle % 360)
        
        # Normalize angle to -180 to 180
        if (angleDiff <= -180):
            angleDiff += 360
        elif (angleDiff > 180):
            angleDiff -= 360
        
        return (dist, angleDiff)
