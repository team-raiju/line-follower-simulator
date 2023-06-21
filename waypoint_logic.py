import os
import pygame
from pygame.math import Vector2
from generate_track import Map
from load_track import LoadMap
from robot import Robot
import math

MAP_FILE_NAME = "map0.png"
MAP_WIDTH_CM = 100
MAP_HEIGHT_CM = 300
MAP_MARGIN_CM = 10
MAP_CM_PER_PIXELS = 3

ROBOT_INIT_POS_X_CM = 11
ROBOT_INIT_POS_Y_CM = 220
ROBOT_INIT_ANGLE = 90

ROBOT_IMAGE = "robot-img.png"
ROBOT_SIZE_X_CM = 14.0 # Width
ROBOT_SIZE_Y_CM = 14.0 # Height
ROTATION_OFFSET_FROM_CENTER_CM = 4.73
WHEELS_DIST_CM = 14.0
WHEELS_RADIUS_CM = 1.0

WAYPOINT_LIST = "waypoints_map0.txt"

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

        self.load_waypoint_list()

        self.last_error = 0
        self.base_speed = 100
        self.kp = 0.357 # 5 / wheels_dist
        self.kd = 1.07  # 10 / wheels_dist

    def load_waypoint_list(self):

        self.waypoint_list = []
        current_dir = os.path.dirname(os.path.abspath(__file__))
        waypoint_list_path = os.path.join(current_dir, "image_conversion", "waypoints", WAYPOINT_LIST)

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

    def draw_map(self):
        self.map.draw_loaded_map()
    
    def draw_timer(self, time):
        text_surface = pygame.font.Font(None, int(13 * MAP_CM_PER_PIXELS)).render(
            "Time: " + "{:.3f}s".format(time), True, (255, 0, 0)
        )
        self.screen.blit(text_surface, (5, 5))

    def calc_error(self, line_sensor_val: list):
        # Similar to center of mass calculation
        num_half_sensors = int(8)

        # Weight list is based on the distance to center of each line sensor
        weight_list = []
        for idx in range(num_half_sensors):
            weight_list.append(self.robot.line_sensor_pos[num_half_sensors + idx].y)

        count_left = 0
        count_right = 0
        sum_left = 0
        sum_right = 0
        for i in range(num_half_sensors):
            count_left += line_sensor_val[i]
            count_right += line_sensor_val[num_half_sensors + i]

            sum_left += weight_list[i] * line_sensor_val[num_half_sensors - 1 - i]
            sum_right += weight_list[i] * line_sensor_val[num_half_sensors + i]

        if count_left == 0:
            count_left = 1
        if count_right == 0:
            count_right = 1
        pos_left = sum_left / count_left
        pos_right = sum_right / count_right

        return pos_left - pos_right
    
    def process_simple_pid(self, line_sensor_values: list):
        error = self.calc_error(line_sensor_values)
        derivative = error - self.last_error
        l_speed = self.pid_base_speed - (error * self.pid_kp + derivative * self.pid_kd)
        r_speed = self.pid_base_speed + (error * self.pid_kp + derivative * self.pid_kd)
        self.last_error = error

        return l_speed, r_speed
    
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
            self.draw_map()

            if (len(self.waypoint_list) > waypoint_idx):
                (dist, angleDiff) = self.trackGoal(self.robot.position, self.waypoint_list[waypoint_idx], self.robot.angle)

                derivative = (angleDiff - self.last_error)
                # print(angleDiff)
                w = - (angleDiff * self.kp + derivative * self.kd)

                self.last_error = angleDiff
                # print(angleDiff)

                self.robot.set_motors_voltage_vel_w(self.base_speed, w)
            else:
                # (dist, angleDiff) = self.trackGoal(self.robot.position, self.waypoint_list[0], self.robot.angle)
                if (not finished):
                    print("Total time: " + str(round(time, 4)) + "s")
                    finished = True
                    self.pid_base_speed = 75
                    self.pid_kp = 25
                    self.pid_kd = 50 
                
                if (stop_counter < 15):
                    line_sensor = self.robot.get_line_sensor(
                        self.screen, self.screen_width, self.screen_height
                    )
                    l_speed, r_speed = self.process_simple_pid(line_sensor)
                    self.robot.set_motors_voltage(l_speed, r_speed)
                    stop_counter += 1 
                    self.pid_base_speed -= 5
                    self.pid_kp -= 1.5
                    self.pid_kd -= 3


                # if dist < 0:
                #     dist = 0
                # self.robot.motor_l.set_voltage(dist/15)
                # self.robot.motor_r.set_voltage(dist/15)


            self.robot.update(dt)

            # Update travalled distance
            if (waypoint_idx < len(self.waypoint_list)):
                if (self.near_waypoint(self.robot.position, self.waypoint_list[waypoint_idx])):
                    waypoint_idx += 1
                    print(waypoint_idx)

            # print("")
            
            # print(self.waypoint_list[1])
            # print(self.robot.position)

            self.draw_timer(time)
            self.robot.display(self.screen)

            pygame.display.flip()
            self.clock.tick(self.ticks)


            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()