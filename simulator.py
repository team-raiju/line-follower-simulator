import pygame
from load_track import LoadMap
from robot import Robot
from helper import Helper as hp

# --- Import the available brains ---
from robot_programs.base_logic import RobotLogic
from robot_programs.manual_logic import ManualLogic
from robot_programs.bitbang_logic import BitBangLogic
from robot_programs.pid_logic import PIDLogic
from robot_programs.map_track_logic import MapTrackLogic
from robot_programs.optimized_run_logic import OptimizedRunLogic
from robot_programs.pure_pursuit_logic import PurePursuitLogic


# --- 1. SELECT THE ROBOT BRAIN ---
# SELECTED_LOGIC: RobotLogic = ManualLogic
# SELECTED_LOGIC: RobotLogic = BitBangLogic
# SELECTED_LOGIC: RobotLogic = PIDLogic
# SELECTED_LOGIC: RobotLogic = MapTrackLogic
# SELECTED_LOGIC: RobotLogic = OptimizedRunLogic
SELECTED_LOGIC: RobotLogic = PurePursuitLogic

# --- 2. MAP & ROBOT PARAMS ---
# Map parameters
MAP_FILE_NAME = "map6.png"
MAP_WIDTH_CM = 303
MAP_HEIGHT_CM = 227
MAP_MARGIN_CM = 25
MAP_CM_PER_PIXELS = 3

# Robot physical parameters
ROBOT_IMAGE = "robot-img-3.png"
ROBOT_SIZE_X_CM = 18.0 
ROBOT_SIZE_Y_CM = 15.0 
ROTATION_OFFSET_FROM_CENTER_CM = 3.72
WHEELS_DIST_CM = 12.0
WHEELS_RADIUS_CM = 1.0

# Robot initial state
ROBOT_INIT_POS_X_CM = 9 
ROBOT_INIT_POS_Y_CM = 135
ROBOT_INIT_ANGLE = 90

# Simulation tick rate
SIM_TICK_RATE = 200

# --- 3. CONFIGURE THE ROBOT LOGIC ---
LOGIC_CONFIG = {
    # Pass physical params the robot logic might need
    'map_cm_per_pixel': MAP_CM_PER_PIXELS,
    'map_margin_cm': MAP_MARGIN_CM,
    'wheels_dist_cm': WHEELS_DIST_CM
}
# -----------------------------

class Simulator:
    def __init__(self):
        # ... (pygame and map init is the same) ...
        pygame.init()
        pygame.display.set_caption("Line Follower Simulator")

        self.map_width_pixels = MAP_WIDTH_CM * MAP_CM_PER_PIXELS
        self.map_height_pixels = MAP_HEIGHT_CM * MAP_CM_PER_PIXELS
        self.margin_pixels = MAP_MARGIN_CM * MAP_CM_PER_PIXELS
        self.screen_width = self.map_width_pixels + (2 * self.margin_pixels)
        self.screen_height = self.map_height_pixels + (2 * self.margin_pixels)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.ticks = SIM_TICK_RATE
        self.exit = False
        self.right_marker_detected = False

        self.map = LoadMap(self.screen)
        self.map.load_map_from_file(
            MAP_FILE_NAME, self.margin_pixels, self.map_width_pixels, self.map_height_pixels
        )

        self.robot = Robot(
            MAP_CM_PER_PIXELS, ROBOT_SIZE_X_CM, ROBOT_SIZE_Y_CM, 
            ROTATION_OFFSET_FROM_CENTER_CM, WHEELS_DIST_CM, WHEELS_RADIUS_CM,
            ROBOT_INIT_POS_X_CM + MAP_MARGIN_CM, ROBOT_INIT_POS_Y_CM + MAP_MARGIN_CM,
            ROBOT_INIT_ANGLE, ROBOT_IMAGE
        )

        self.robot_logic = SELECTED_LOGIC(**LOGIC_CONFIG)
    
    def run(self):
        while not self.exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            dt = self.clock.get_time() / 1000

            self.screen.fill((0, 0, 0))
            self.map.draw_loaded_map()

            # --- SENSE ---
            line_sensor = self.robot.get_line_sensor(self.screen, self.screen_width, self.screen_height)

            # --- THINK ---
            # Create the state dictionary to pass to the brain
            robot_state = {
                'position_cm': self.robot.estimated_position_cm,
                'angle_deg': self.robot.estimated_angle,
                'total_dist_cm': self.robot.estimated_total_dist_cm,
                'angular_velocity': self.robot.angular_velocity,
                'white_val': self.robot.white_val,
                'black_val': self.robot.black_val,
                'line_sensor_positions': self.robot.line_sensor_pos[0:19]
            }

            l_speed, r_speed = self.robot_logic.process_tick(dt, line_sensor, robot_state)

            if not self.right_marker_detected and self.robot_logic.first_right_marker():
                print("First right marker detected by the robot logic.")
                self.right_marker_detected = True
                self.robot.reset_relative_position()
                print(self.robot.estimated_position_cm)


            # --- ACT ---
            self.robot.set_motors_voltage(l_speed, r_speed)
            self.robot.update(dt)

            # --- RENDER ---
            hp.draw_timer(self.screen, self.robot_logic.get_time(), MAP_CM_PER_PIXELS)
            self.robot.display(self.screen)
            
            pygame.display.flip()
            self.clock.tick(self.ticks)

        pygame.quit()


if __name__ == "__main__":
    game = Simulator()
    game.run()