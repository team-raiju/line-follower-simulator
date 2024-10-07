import os
import pygame
from pygame.math import Vector2
from load_track import LoadMap
from robot import Robot
import math
from helper import Helper as hp
from helper import PIDFunctions as pid
import sys
import numpy as np

MAP_FILE_NAME = "map2.png"
MAP_WIDTH_CM = 186
MAP_HEIGHT_CM = 354
MAP_MARGIN_CM = 25
MAP_CM_PER_PIXELS = 2

ROBOT_INIT_POS_X_CM = 178 
ROBOT_INIT_POS_Y_CM = 75
ROBOT_INIT_ANGLE = 270
MIN_LEFT_MARKER_COUNTER = 26

ROBOT_IMAGE = "robot-img-3.png"
ROBOT_SIZE_X_CM = 18.0 # Width
ROBOT_SIZE_Y_CM = 15.0 # Height
ROTATION_OFFSET_FROM_CENTER_CM = 3.72
WHEELS_DIST_CM = 12.0
WHEELS_RADIUS_CM = 1.0

DEFAULT_WAYPOINT_LIST = "maps/mapping_data/map2/map2_track.txt"

INIT_BASE_SPEED = 75
INIT_KP = 0.416 # 5 / wheels_dist
INIT_KD = 0.833 # 10 / wheels_dist

# Pure pursuit parameters
LOOK_AHEAD = 40
MAX_WAYPOINTS_AHEAD = 4 

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Line Follower")

        self.map_width_pixels = MAP_WIDTH_CM * MAP_CM_PER_PIXELS
        self.map_height_pixels = MAP_HEIGHT_CM * MAP_CM_PER_PIXELS

        margin_pixels = MAP_MARGIN_CM * MAP_CM_PER_PIXELS
        self.screen_width = self.map_width_pixels + (2 * margin_pixels)
        self.screen_height = self.map_height_pixels + (2 * margin_pixels)

        self.screen = pygame.display.set_mode((self.screen_width , self.screen_height))
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
        self.map.load_map_from_file(MAP_FILE_NAME, margin_pixels, self.map_width_pixels, self.map_height_pixels)

        if (len(sys.argv) < 2):
            print("Using default track")
            self.load_waypoint_list(DEFAULT_WAYPOINT_LIST)
        else:
            self.load_waypoint_list(sys.argv[1])


        self.last_error = 0
        self.base_speed = INIT_BASE_SPEED
        self.kp = INIT_KP
        self.kd = INIT_KD


    def load_waypoint_list(self, waypoints_file_name):

        self.waypoint_list = []
        current_dir = os.path.dirname(os.path.abspath(__file__))
        waypoint_list_path = os.path.join(current_dir, waypoints_file_name)

        with open(waypoint_list_path, "r") as f:
            for line in f:
                x_cm, y_cm = line.strip().split(",")
                x_pixel = (float(x_cm) + MAP_MARGIN_CM) * MAP_CM_PER_PIXELS
                y_pixel = (float(y_cm) + MAP_MARGIN_CM) * MAP_CM_PER_PIXELS
                point = Vector2(int(x_pixel), int(y_pixel))
                self.waypoint_list.append(point)

    def near_waypoint(self, point: Vector2, point_2: Vector2):
        distance = point.distance_to(point_2)
        max_dist_cm = 15
        if (abs(distance) < max_dist_cm * MAP_CM_PER_PIXELS):
            return True
        return False
    
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
    
    def get_estimated_pos_pixel(self):
        position_cm = self.robot.estimated_position_cm + Vector2(0, 0).rotate(-self.robot.estimated_angle)
        pixel_x = position_cm.x * MAP_CM_PER_PIXELS
        pixel_y = position_cm.y * MAP_CM_PER_PIXELS
        return Vector2(pixel_x, pixel_y)

    
    def run(self):
        waypoint_idx = 0
        time = 0
        finished = False
        stop_counter = 0
        self.w_pid_calc = pid(0, 1, 2, 0.0)


        while not self.exit:
            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            dt = self.clock.get_time() / 1000
            if (not finished):
                time += dt 

            #Draw
            self.screen.fill((0, 0, 0))
            self.map.draw_loaded_map()

            # Draw all waypoints
            # for i in range(len(self.waypoint_list)):
            #     pygame.draw.circle(self.screen, (255, 0, 0), (int(self.waypoint_list[i].x), int(self.waypoint_list[i].y)), 5)


            if (waypoint_idx < len(self.waypoint_list) - 1):
                # estimated_robot_pos = self.get_estimated_pos_pixel()
                estimated_robot_pos = self.robot.position
                (dist, angleDiff) = self.trackGoal(estimated_robot_pos, self.waypoint_list[waypoint_idx], self.robot.estimated_angle)
                
                R = 10000
                if(abs(angleDiff) > 1):
                    R = LOOK_AHEAD / (2 * math.sin(math.radians(angleDiff)))
 
                ## Radius center point
                # center_x = estimated_robot_pos.x - R * math.sin(math.radians(self.robot.estimated_angle + 90))
                # center_y = estimated_robot_pos.y + R * math.cos(math.radians(self.robot.estimated_angle + 90))
                # pygame.draw.circle(self.screen, (0, 0, 255), (int(center_x), int(center_y)), 3)
                # pygame.draw.circle(self.screen, (255, 0, 0), (int(center_x), int(center_y)), abs(R), 1)

                ## Draw line from center to robot to the next goal
                # pygame.draw.line(self.screen, (255, 0, 255), (self.robot.position.x, self.robot.position.y), (self.waypoint_list[waypoint_idx].x, self.waypoint_list[waypoint_idx].y), 4)

                ## Draw look ahead search distance
                # pygame.draw.circle(self.screen, (0, 255, 0), (int(self.robot.position.x), int(self.robot.position.y)), LOOK_AHEAD, 1)

                base_rot_ratio = (WHEELS_DIST_CM / (2 * R)) * self.base_speed
                target_w = (2 * base_rot_ratio) / (WHEELS_DIST_CM * 0.01) # rad/s
                error_w = target_w - self.robot.angular_velocity

                # Angular speed error
                w_pid = self.w_pid_calc.pid_process(error_w)
                alpha = ((WHEELS_DIST_CM * 0.01) * w_pid) / 2

                
                self.robot.set_motors_voltage(self.base_speed + base_rot_ratio + alpha, self.base_speed - base_rot_ratio - alpha)
            else:
                if (not finished):
                    self.robot.set_motors_voltage(0, 0)
                    print("Total time: " + str(round(time, 4)) + "s")
                    finished = True
            
            self.robot.update(dt)

            # Update travalled distance
            if (waypoint_idx < len(self.waypoint_list)):

                # Find frontal point
                front_vector = Vector2(25, 0)
                point_front = self.robot.position + front_vector.rotate(-self.robot.angle)

                # Find look ahead point
                min_diff_modulo = 1000
                look_ahead_point = waypoint_idx
                for i in range(MAX_WAYPOINTS_AHEAD):
                    if (waypoint_idx + i >= len(self.waypoint_list)):
                        look_ahead_point = len(self.waypoint_list) - 1
                        break
                    diff = point_front.distance_to(self.waypoint_list[waypoint_idx + i]) - LOOK_AHEAD
                    if (diff < 0 and abs(diff) < min_diff_modulo):
                        min_diff_modulo = abs(diff)
                        look_ahead_point = waypoint_idx + i


                waypoint_idx = look_ahead_point
            else:
                waypoint_idx = len(self.waypoint_list) - 1


            print("Waypoint: " + str(waypoint_idx) + " of " + str(len(self.waypoint_list)))
            hp.draw_timer(self.screen, time, MAP_CM_PER_PIXELS)
            self.robot.display(self.screen)

            pygame.display.flip()
            self.clock.tick(self.ticks)


            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()