from abc import ABC, abstractmethod

class RobotLogic(ABC):
    """
    Abstract Base Class for all robot logic controllers
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

        Returns:
            (float, float): The calculated left_speed and right_speed.
        """
        pass

    @abstractmethod
    def get_time(self) -> float:
        """
        Get time passed from the robot perspective
        """
        pass

    @abstractmethod
    def first_right_marker(self) -> bool:
        """
        Indicate if the first right marker has been detected.
        """
        pass