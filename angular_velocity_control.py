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

INIT_KP = 40
INIT_KD = 55

DEFAULT_RADIUS_LIST = "maps/mapping_data/map5/map5_radius_edit.txt"

TRACK_POINTS_DIST_CM = 5

BASE_VEL_M_S = 0.5

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
    
    
    def radius_to_velocity(self, radius):
        rot_ratio = ((WHEELS_DIST_CM * 0.01) / (2 * (radius * 0.01))) * BASE_VEL_M_S # m/s -> wheel ratio to subtract from right wheel and add to left wheel
        
        return rot_ratio

    def create_velocity_table(self):

        # TODO Filter big radius inside small radius sequency
        radius_list = []
        current_dir = os.path.dirname(os.path.abspath(__file__))

        file_name = DEFAULT_RADIUS_LIST
        if (len(sys.argv) >= 2):
            file_name = sys.argv[1]

        radius_list_path = os.path.join(current_dir, file_name)

        with open(radius_list_path, "r") as f:
            for line in f:
                radius_val = float(line.strip())
                radius_list.append(radius_val)

        for radius in radius_list:
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
        base_rotation = self.rot_ratio_table[0]

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


            if (not finished):
                total_dist = float(self.robot.total_dist_cm)
                if (total_dist > (last_dist_saved + TRACK_POINTS_DIST_CM)):
                    vel_tbl_idx += 1
                    last_dist_saved = total_dist
                    base_rotation = self.rot_ratio_table[vel_tbl_idx]
                    print(vel_tbl_idx)


            vel_m_s = (self.robot.mot_vel_l + self.robot.mot_vel_r) / 2

            # rot_ratio = ((WHEELS_DIST_CM * 0.01) / (2 * R)) * vel_m_s # m/s -> wheel ratio to subtract from right wheel and add to left wheel

            target_w = (2 * base_rotation) / (WHEELS_DIST_CM * 0.01) # rad/s

            #print("rot_ratio: " + str(base_rotation) + " vel: " + str(vel_m_s), " target_w: " + str(target_w))
            #print(self.robot.angular_velocity)

            #TODO add pid control for target angular velocity and current angular velocity
                
            self.robot.set_motor_vel_inf(BASE_VEL_M_S - base_rotation, BASE_VEL_M_S + base_rotation)
            
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