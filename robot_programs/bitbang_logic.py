from .base_logic import RobotLogic

class BitBangLogic(RobotLogic):

    def __init__(self, **kwargs):
        self.base_speed = kwargs.get('base_speed', 35)
        self.time = 0.0
        print("BitBangLogic initialized.")

    def get_time(self):
        return self.time
    
    def first_right_marker(self) -> bool:
        return self.right_marker_counter >= 1

    def process_tick(self, dt: float, line_sensor_data: list, robot_state: dict):
        self.time += dt
        
        # We read the two outermost sensors from the main array
        # line_sensor_data[0] is far-left
        # line_sensor_data[15] is far-right
        
        is_white_left = (line_sensor_data[0] == robot_state['white_val'])
        is_white_right = (line_sensor_data[15] == robot_state['white_val'])
        
        l_speed, r_speed = self.base_speed, self.base_speed

        if is_white_left:
            # Line is on the left, turn left
            l_speed = 0
            r_speed = self.base_speed
        elif is_white_right:
            # Line is on the right, turn right
            l_speed = self.base_speed
            r_speed = 0
        
        return l_speed, r_speed