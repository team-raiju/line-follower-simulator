from .base_logic import RobotLogic
from helper import PIDFunctions as pid
from helper import CountMarkers as cm
from helper import Helper as hp


class PIDLogic(RobotLogic):

    def __init__(self, **kwargs):
        base_speed = kwargs.get('base_speed', 70)
        kp = kwargs.get('kp', 35)
        kd = kwargs.get('kd', 50)
        ki = 0.0
        self.min_left_marker_counter = kwargs.get('min_left_marker_counter', 50)
        
        self.pid_calc = pid(base_speed, kp, kd, ki)
        self.count_markers = cm()
        
        self.left_marker_counter = 0
        self.right_marker_counter = 0
        
        self.time = 0.0
        self.finished = False
        self.last_error = 0.0

    def get_time(self):
        return self.time

    def first_right_marker(self) -> bool:
        return self.right_marker_counter >= 1

    def process_tick(self, dt: float, line_sensor_data: list, robot_state: dict):
        # Timekeeping
        if not self.finished:
            self.time += dt

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
            elif self.left_marker_counter > self.min_left_marker_counter:
                if not self.finished:
                    print("Total time: " + str(round(self.time, 4)) + "s")
                    self.finished = True
                    self.pid_calc = pid(15, 3.5, 2)

        # Calculate Motor Output
        l_speed, r_speed = self.pid_calc.simple_pid(error)
        
        return l_speed, r_speed