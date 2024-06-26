import os
import pygame
from pygame.math import Vector2
from generate_track import Map
from load_track import LoadMap
from robot import Robot
import math
from helper import Helper as hp
from helper import PIDFunctions as pid
from helper import CountMarkers as cm
import sys

MAP_FILE_NAME = "map5.png"
MAP_WIDTH_CM = 651
MAP_HEIGHT_CM = 317
MAP_MARGIN_CM = 25
MAP_CM_PER_PIXELS = 2

ROBOT_INIT_POS_X_CM = 125 
ROBOT_INIT_POS_Y_CM = 308
ROBOT_INIT_ANGLE = 180
MIN_LEFT_MARKER_COUNTER = 33


ROBOT_IMAGE = "robot-img-3.png"
ROBOT_SIZE_X_CM = 18.0 # Width
ROBOT_SIZE_Y_CM = 15.0 # Height
ROTATION_OFFSET_FROM_CENTER_CM = 3.72
WHEELS_DIST_CM = 12.0
WHEELS_RADIUS_CM = 1.0

INIT_KP = 2.6
INIT_KD = 2

DEFAULT_RADIUS_LIST = "maps/mapping_data/map5/map5_radius.txt"

TRACK_POINTS_DIST_CM = 5

BASE_VEL_M_S = 4

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Line Follower")

        self.map_width_pixels = MAP_WIDTH_CM * MAP_CM_PER_PIXELS
        self.map_height_pixels = MAP_HEIGHT_CM * MAP_CM_PER_PIXELS

        margin_pixels = MAP_MARGIN_CM * MAP_CM_PER_PIXELS
        self.screen_width = self.map_width_pixels + (2 * margin_pixels)
        self.screen_height = self.map_height_pixels + (2 * margin_pixels)

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.ticks = 150
        self.exit = False

        self.robot = Robot(
            MAP_CM_PER_PIXELS,
            ROBOT_SIZE_X_CM,
            ROBOT_SIZE_Y_CM,
            ROTATION_OFFSET_FROM_CENTER_CM,
            WHEELS_DIST_CM,
            WHEELS_RADIUS_CM,
            ROBOT_INIT_POS_X_CM + MAP_MARGIN_CM,
            ROBOT_INIT_POS_Y_CM + MAP_MARGIN_CM,
            ROBOT_INIT_ANGLE,
            ROBOT_IMAGE,
        )

        self.map = LoadMap(self.screen)
        self.map.load_map_from_file(
            MAP_FILE_NAME, margin_pixels, self.map_width_pixels, self.map_height_pixels
        )

        self.left_marker_counter = 0
        self.right_marker_counter = 0

        self.rot_ratio_table = []
        self.radius_list = []

    
    
    def radius_to_velocity(self, radius):
        rot_ratio = ((WHEELS_DIST_CM * 0.01) / (2 * (radius * 0.01))) * BASE_VEL_M_S # m/s -> wheel ratio to subtract from right wheel and add to left wheel
        
        return rot_ratio

    def create_velocity_table(self):

        # TODO Filter big radius inside small radius sequency
        current_dir = os.path.dirname(os.path.abspath(__file__))

        file_name = DEFAULT_RADIUS_LIST
        if (len(sys.argv) >= 2):
            file_name = sys.argv[1]

        radius_list_path = os.path.join(current_dir, file_name)

        with open(radius_list_path, "r") as f:
            for line in f:
                radius_val = float(line.strip())
                self.radius_list.append(radius_val)

        for radius in self.radius_list:
            ratio = self.radius_to_velocity(radius)
            self.rot_ratio_table.append(ratio)
   
        # Delay filter
        #self.shift_velocity_table(6)

        # Process acceleration
        #self.velocity_process_acceleration(10, -10)

    
    def trackGoal(self, currentPos: Vector2, goal: Vector2, robot_angle):
        dist = currentPos.distance_to(goal)

        dx = goal.x - currentPos.x
        dy = goal.y - currentPos.y

        # calculate the angle in radians and convert to degrees
        angleDiffRaw = (math.atan2(dy, dx) * 180 / math.pi)

        angleDiff = angleDiffRaw - (-robot_angle % 360)
        if (angleDiff <= -180):
            angleDiff += 360
        
        return (dist, angleDiff)


    def run(self):
        time = 0
        finished = False
        last_dist_saved = 0
        vel_tbl_idx = 0
        self.create_velocity_table()
        count_markers = cm()
        self.pid_calc = pid(0, INIT_KP, INIT_KD, 0)
        self.vel_pid_calc = pid(0, 0.0, 0, 0.00)
        self.w_pid_calc = pid(0, 1, 0.1, 0.0)
        loop = 0
        error_w_sum = 0

        while not self.exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            dt = self.clock.get_time() / 1000
            if (not finished):
                time += dt 

            self.screen.fill((0, 0, 0))
            self.map.draw_loaded_map()
            hp.draw_timer(self.screen, time, MAP_CM_PER_PIXELS)

            # Line sensor error
            line_sensor = self.robot.get_line_sensor(self.screen, self.screen_width, self.screen_height)
            line_sensor = hp.filter_line(line_sensor, self.robot.white_val, self.robot.black_val)

            error = pid.calc_error(line_sensor, self.robot.line_sensor_pos[0:16])
            if (error == -99):
                error = self.pid_calc.get_last_error()

            sensor_rot_ratio = self.pid_calc.pid_process(error)

            # Linear speed error
            speed_error = BASE_VEL_M_S - self.robot.velocity_m_s.x
            vel_pid = BASE_VEL_M_S + self.vel_pid_calc.pid_process(speed_error)

            if (not finished):
                total_dist = float(self.robot.total_dist_cm)
                if (total_dist > (last_dist_saved + TRACK_POINTS_DIST_CM)):
                    vel_tbl_idx += 1
                    last_dist_saved = total_dist
                    # print(vel_tbl_idx)


            # Angular target speed
            base_rot_ratio = ((WHEELS_DIST_CM * 0.01) / (2 * (self.radius_list[vel_tbl_idx] * 0.01))) * self.robot.velocity_m_s.x
            target_w = (2 * base_rot_ratio) / (WHEELS_DIST_CM * 0.01) # rad/s
            error_w = target_w - self.robot.angular_velocity

            # Angular speed error
            w_pid = self.w_pid_calc.pid_process(error_w)
            alpha = ((WHEELS_DIST_CM * 0.01) * w_pid) / 2


            # print("mean = " + str(error_w_sum / loop) + " target_w = " + str(target_w) + " w = " + str(self.robot.angular_velocity) + "vel = " + str(self.robot.velocity_m_s.x))
            

            # print("rot_ratio: " + str(self.robot.angular_velocity) + " vel: " + str(self.robot.velocity_m_s.x), " target_w: " + str(target_w))
            #print(self.robot.angular_velocity)

            self.robot.set_motors_speed_m_s(vel_pid - (base_rot_ratio + sensor_rot_ratio + alpha), vel_pid + (base_rot_ratio + sensor_rot_ratio + alpha))
                
            
            #Draw
            self.robot.update(dt)
            self.robot.display(self.screen)
            # self.robot.display_line_sensor(self.screen)
            pygame.display.flip()

            self.clock.tick(self.ticks)


            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()