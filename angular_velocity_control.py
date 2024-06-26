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

MAP_FILE_NAME = "circles.png"
MAP_WIDTH_CM = 200
MAP_HEIGHT_CM = 200
MAP_MARGIN_CM = 0
MAP_CM_PER_PIXELS = 2

ROBOT_INIT_POS_X_CM = 55
ROBOT_INIT_POS_Y_CM = 150
ROBOT_INIT_ANGLE = 90
MIN_LEFT_MARKER_COUNTER = 50

ROBOT_IMAGE = "robot-img-3.png"
ROBOT_SIZE_X_CM = 18.0 # Width
ROBOT_SIZE_Y_CM = 15.0 # Height
ROTATION_OFFSET_FROM_CENTER_CM = 3.72
WHEELS_DIST_CM = 12.0
WHEELS_RADIUS_CM = 1.0

INIT_KP = 40
INIT_KD = 55

DEFAULT_RADIUS_LIST = "maps/mapping_data/map4/map4_radius.txt"

TRACK_POINTS_DIST_CM = 5

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

        self.velocity_table = []
    
    
    def radius_to_velocity(self, radius):
        velocity = 45
        if(radius < 20):
            velocity = 40
        elif(radius < 30):
            velocity = 50
        elif(radius < 50):
            velocity = 70
        elif(radius < 70):
            velocity = 90
        else:
            velocity = 100
        
        return velocity

    def shift_velocity_table(self, shift_size):
        for i in range(shift_size, len(self.velocity_table)):
            self.velocity_table[i - shift_size] = self.velocity_table[i]
        
        for i in range(shift_size):
            self.velocity_table[-i - 1] = 30

        return self.velocity_table


    def velocity_process_acceleration(self, max_v_diff_positive, min_v_diff_negative):
        # TODO Remove dist_between points dependency using t = p_dist/v-diff
        for i in range(len(self.velocity_table) - 1):
            v_diff = self.velocity_table[i + 1] - self.velocity_table[i]
            if (v_diff > max_v_diff_positive):
                self.velocity_table[i + 1] = self.velocity_table[i] + max_v_diff_positive
            elif (v_diff < min_v_diff_negative):
                self.velocity_table[i + 1] = self.velocity_table[i] + min_v_diff_negative
    
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
                radius_list.append(abs(radius_val))

        for radius in radius_list:
            velocity = self.radius_to_velocity(radius)
            self.velocity_table.append(velocity)
   
        # Delay filter
        self.shift_velocity_table(6)

        # Process acceleration
        self.velocity_process_acceleration(10, -10)

    
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
        base_speed = self.velocity_table[0]
        count_markers = cm()
        self.pid_calc = pid(base_speed, INIT_KP, INIT_KD)
        vel = 3

        while not self.exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            dt = self.clock.get_time() / 1000
            if (not finished):
                time += dt 

            self.screen.fill((0, 0, 0))
            self.map.draw_loaded_map()
            hp.draw_timer(self.screen, vel, MAP_CM_PER_PIXELS)

            R = -40 * 0.01 # cm
            # vel += 0.1
            # vel = min(vel, 100)
            vel_m_s = (self.robot.mot_vel_l + self.robot.mot_vel_r) / 2

            rot_ratio = ((WHEELS_DIST_CM * 0.01) / (2 * R)) * vel_m_s # m/s -> wheel ratio to subtract from right wheel and add to left wheel

            target_w = (2 * rot_ratio) / (WHEELS_DIST_CM * 0.01) # rad/s

            print("rot_ratio: " + str(rot_ratio) + " vel: " + str(vel_m_s), " target_w: " + str(target_w))
            print(self.robot.angular_velocity)
                
            self.robot.set_motor_vel_inf(vel - rot_ratio, vel + rot_ratio)
            
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