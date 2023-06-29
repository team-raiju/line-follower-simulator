import os
import pygame
from pygame.math import Vector2
from load_track import LoadMap
from robot import Robot
import math
from helper import Helper as hp
from helper import PIDFunctions as pid
import sys

MAP_FILE_NAME = "map5.png"
MAP_WIDTH_CM = 651
MAP_HEIGHT_CM = 317
MAP_MARGIN_CM = 25
MAP_CM_PER_PIXELS = 2

ROBOT_INIT_POS_X_CM = 125 
ROBOT_INIT_POS_Y_CM = 309
ROBOT_INIT_ANGLE = 180
MIN_LEFT_MARKER_COUNTER = 33

ROBOT_IMAGE = "robot-img-2.png"
ROBOT_SIZE_X_CM = 19.0 # Width
ROBOT_SIZE_Y_CM = 14.0 # Height
ROTATION_OFFSET_FROM_CENTER_CM = 4.73
WHEELS_DIST_CM = 14.0
WHEELS_RADIUS_CM = 1.0

DEFAULT_WAYPOINT_LIST = "image_conversion/waypoints/map2_opt_waypoints.txt"

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

        print(len(sys.argv))
        if (len(sys.argv) < 2):
            print("Using default track")
            self.load_waypoint_list(DEFAULT_WAYPOINT_LIST)
        else:
            self.load_waypoint_list(sys.argv[1])


        self.last_error = 0
        self.base_speed = 100
        self.kp = 0.357 # 5 / wheels_dist
        self.kd = 1.07  # 10 / wheels_dist

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

            if (len(self.waypoint_list) > waypoint_idx):
                estimated_robot_pos = self.get_estimated_pos_pixel()
                (dist, angleDiff) = self.trackGoal(estimated_robot_pos, self.waypoint_list[waypoint_idx], self.robot.estimated_angle)

                derivative = (angleDiff - self.last_error)
                # print(angleDiff)
                w = - (angleDiff * self.kp + derivative * self.kd)

                self.last_error = angleDiff
                # print(angleDiff)

                self.robot.set_motors_voltage_vel_w(self.base_speed, w)
            else:
                if (not finished):
                    print("Total time: " + str(round(time, 4)) + "s")
                    finished = True
                    self.pid_base_speed = self.base_speed - 15
                    self.pid_kp = 25
                    self.pid_kd = 50 
                    self.pid_calc = pid(self.pid_base_speed, self.pid_kp, self.pid_kd)
                
                if (stop_counter < 45):
                    stop_counter += 1 
                    
                    line_sensor = self.robot.get_line_sensor(self.screen, self.screen_width, self.screen_height)
                    line_sensor = hp.filter_line(line_sensor, self.robot.white_val, self.robot.black_val)

                    error = pid.calc_error(line_sensor, self.robot.line_sensor_pos[0:16])
                    if (error == -99):
                        error = self.pid_calc.get_last_error()

                    l_speed, r_speed = self.pid_calc.simple_pid(error)
                    self.robot.set_motors_voltage(l_speed, r_speed)
                    
                    self.pid_base_speed -= 1.5
                    if (self.pid_base_speed < 0):
                        self.pid_base_speed = 0
                    self.pid_kp -= 0.5
                    self.pid_kd -= 1
                    self.pid_calc = pid(self.pid_base_speed, self.pid_kp, self.pid_kd)
                else:
                    self.robot.set_motors_voltage(0, 0)




            self.robot.update(dt)

            # Update travalled distance
            if (waypoint_idx < len(self.waypoint_list)):
                estimated_robot_pos = self.get_estimated_pos_pixel()
                if (self.near_waypoint(estimated_robot_pos, self.waypoint_list[waypoint_idx])):
                    waypoint_idx += 1
                    print(waypoint_idx)


            hp.draw_timer(self.screen, time, MAP_CM_PER_PIXELS)
            self.robot.display(self.screen)

            pygame.display.flip()
            self.clock.tick(self.ticks)


            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()