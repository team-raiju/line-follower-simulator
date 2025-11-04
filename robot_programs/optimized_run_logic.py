import os

from .base_logic import RobotLogic
from helper import PIDFunctions as pid
from helper import CountMarkers as cm
from helper import Helper as hp

# Logic-specific constants
MIN_LEFT_MARKER_COUNTER = 40
TRACK_POINTS_DIST_CM = 5.0


RADIUS_LIST = "../maps/mapping_data/map6/map6_radius.txt"

class OptimizedRunLogic(RobotLogic):
    """
    A robot logic that uses a PID controller to follow a line.
    """
    def __init__(self, **kwargs):
        start_speed = kwargs.get('start_speed', 80)

        self.kp = kwargs.get('kp', 35)
        self.kd = kwargs.get('kd', 50)
        
        self.pid_calc = pid(start_speed, self.kp, self.kd)
        self.count_markers = cm()
        
        self.left_marker_counter = 0
        self.right_marker_counter = 0
        
        self.time = 0.0
        self.finished = False
        self.last_error = 0.0
        self.velocity_table = []
        self.last_update_dist = 0
        self.vel_idx = 0
        self.create_velocity_table()


    def get_time(self):
        return self.time
    
    def first_right_marker(self) -> bool:
        return self.right_marker_counter >= 1

    def process_tick(self, dt: float, line_sensor_data: list, robot_state: dict):
        # Timekeeping
        if not self.finished:
            self.time += dt
        
        if self.first_right_marker():
            total_dist = float(robot_state['total_dist_cm'])
            if total_dist > (self.last_update_dist + TRACK_POINTS_DIST_CM):
                self.vel_idx += 1
                if (self.vel_idx >= len(self.velocity_table)):
                    self.vel_idx = len(self.velocity_table) - 1
                new_vel = self.velocity_table[self.vel_idx]
                print(f"Updating velocity to: {new_vel} at distance {total_dist} cm")

                self.pid_calc.set_base_speed(new_vel)
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
            elif self.left_marker_counter > MIN_LEFT_MARKER_COUNTER:
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

    
    def filter_velocity_table(self):
        for i in range(1, len(self.velocity_table) - 1):
            previous_velocity = self.velocity_table[i - 1]
            current_velocity = self.velocity_table[i]
            next_velocity = self.velocity_table[i + 1]

            if (previous_velocity == next_velocity) and (current_velocity != previous_velocity):
                self.velocity_table[i] = previous_velocity

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
        velocity = 60
        if(radius < 20):
            velocity = 60
        elif(radius < 30):
            velocity = 60
        elif(radius < 50):
            velocity = 60
        elif(radius < 70):
            velocity = 100
        else:
            velocity = 100
        
        return velocity