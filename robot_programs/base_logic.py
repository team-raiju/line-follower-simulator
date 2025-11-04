# file: robot_brains/base_brain.py

from abc import ABC, abstractmethod

class RobotLogic(ABC):
    """
    Abstract Base Class for all robot logic controllers ("brains").
    It defines the common interface that the simulator will use.
    """
    
    @abstractmethod
    def __init__(self, **kwargs):
        """
        All brains must be initializable. 
        We use **kwargs to allow for different initialization parameters.
        """
        pass

    @abstractmethod
    def process_tick(self, dt: float, line_sensor_data: list, robot_state: dict):
        """
        This is the main "think" method that the simulator will call on each frame.
        It must take sensor data and the robot's state and return motor speeds.

        Args:
            dt (float): The time delta since the last frame.
            line_sensor_data (list): A list of values from the line sensors.
            robot_state (dict): A dictionary containing the robot's current state.
                Keys include:
                'position_cm': Estimated position (Vector2)
                'angle_deg': Estimated angle in degrees (float)
                'total_dist_cm': Estimated total distance travelled (float)
                'angular_velocity': Current angular velocity in rad/s (float)
                'white_val': The value representing white.
                'black_val': The value representing black.
                'line_sensor_positions': List of sensor position vectors.
        
        Returns:
            (float, float): The calculated left_speed and right_speed.
        """
        pass

    @abstractmethod
    def get_time(self) -> float:
        """
        The simulator needs a way to get the current time from the brain's perspective.
        """
        pass

    @abstractmethod
    def first_right_marker(self) -> bool:
        """
        Optional method to indicate if the first right marker has been detected.
        Default implementation returns False.
        """
        pass