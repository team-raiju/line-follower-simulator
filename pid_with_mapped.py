import os
import pygame
from pygame.math import Vector2
from generate_track import Map
from load_track import LoadMap
from robot import Robot
import math

MAP_FILE_NAME = "map5.png"
MAP_WIDTH_CM = 651
MAP_HEIGHT_CM = 317
MAP_MARGIN_CM = 25
MAP_CM_PER_PIXELS = 2

ROBOT_INIT_POS_X_CM = 150 
ROBOT_INIT_POS_Y_CM = 334
ROBOT_INIT_ANGLE = 180
MIN_LEFT_MARKER_COUNTER = 33

ROBOT_IMAGE = "robot-img.png"
ROBOT_SIZE_X_CM = 14.0 # Width
ROBOT_SIZE_Y_CM = 14.0 # Height
ROTATION_OFFSET_FROM_CENTER_CM = 4.73
WHEELS_DIST_CM = 14.0
WHEELS_RADIUS_CM = 1.0

radius_list = [5000, 5000, 5000, 5000, 53.66666666666662, 53.66666666666651, 53.66666666666655, 53.66666666666662, 53.66666666666655, 32.19999999999985, 83.99999999999949, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 53.66666666666656, 53, 53.66666666666568, 53.66666666666597, 53.66666666666568, 53.66666666666508, 53.666666666664824, 53, 53.666666666666615, 32.199999999999086, 53.66666666666484, 41.99999999999967, 32.199999999999065, 53.66666666666568, 32.199999999999584, 10.733333333333086, 32.19999999999953, 83.99999999999825, 32.19999999999953, 32.19999999999923, 32.199999999998695, 32.199999999998695, 27.999999999998867, 32.199999999998695, 83.99999999999667, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 53.66666666666455, 53.66666666666455, 53.66666666666455, 53.66666666666455, 83.99999999999667, 53.66666666666453, 53.66666666666449, 53.66666666666449, 32, 32.199999999998695, 12.384615384614895, 17.888888888888236, 10, 10, 10, 10, 10.733333333332935, 7.666666666666358, 6.999999999999725, 10.733333333332904, 53.66666666666449, 22.99999999999907, 14.636363636363049, 11.999999999999526, 14.636363636363045, 53.66666666666449, 53.66666666666449, 53.66666666666449, 53.66666666666449, 32.199999999998745, 41.99999999999846, 53.6666666666647, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 53.6666666666647, 53.6666666666647, 32.199999999998795, 53.66666666666449, 41.9999999999983, 32.199999999998695, 32.199999999998695, 53.66666666666449, 32.199999999998695, 32.19999999999873, 53.66666666666455, 53.66666666666455, 5000, 83.99999999999667, 53.66666666666455, 5000, 53.66666666666455, 32.19999999999873, 5000, 53.66666666666455, 53.66666666666455, 5000, 83.99999999999667, 41.99999999999834, 41.99999999999834, 5000, 53.66666666666453, 41.99999999999834, 53.66666666666455, 53.66666666666455, 53.66666666666455, 53.66666666666455, 83.9999999999966, 5000, 83.9999999999966, 53.66666666666453, 53.66666666666455, 5000, 5000, 53.66666666666455, 53.66666666666449, 53.66666666666449, 83.9999999999966, 53.66666666666449, 83.99999999999665, 5000, 5000, 53.66666666666451, 53.66666666666449, 53.66666666666449, 5000, 5000, 53.66666666666449, 5000, 5000, 53.66666666666449, 5000, 53.66666666666449, 5000, 5000, 5000, 5000, 5000, 53.66666666666449, 53.66666666666449, 22.99999999999907, 12.384615384614913, 32.199999999998816, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 53.6666666666647, 32.199999999998816, 17.888888888888236, 17.888888888888236, 17.888888888888236, 14.636363636363102, 22.999999999999158, 14.636363636363102, 32.199999999998816]


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
        self.ticks = 180
        self.exit = False

        self.robot = Robot(MAP_CM_PER_PIXELS, ROBOT_SIZE_X_CM,           \
                        ROBOT_SIZE_Y_CM, ROTATION_OFFSET_FROM_CENTER_CM, \
                        WHEELS_DIST_CM, WHEELS_RADIUS_CM,                \
                        ROBOT_INIT_POS_X_CM, ROBOT_INIT_POS_Y_CM,        \
                        ROBOT_INIT_ANGLE, ROBOT_IMAGE)
    

        self.map = LoadMap(self.screen)
        self.map.load_map_from_file(MAP_FILE_NAME, margin_pixels, self.map_width_pixels, self.map_height_pixels)

        self.left_marker_counter = 0
        self.right_marker_counter = 0
        self.last_left_marker = False
        self.last_right_marker = False
        self.last_error = 0
        
        self.base_speed = 80
        self.kp = 43
        self.kd = 60 

        self.velocity_table = []
    
    def draw_map(self):
        self.map.draw_loaded_map()
    
    def draw_timer(self, time):
        text_surface = pygame.font.Font(None, 36).render("Time: " + "{:.3f}s".format(time), True, (255, 0, 0))
        self.screen.blit(text_surface, (10, 10))
    
    def radius_to_velocity(self, radius):
        velocity = 45
        if(radius < 20):
            velocity = 40
        elif(radius < 30):
            velocity = 50
        elif(radius < 50):
            velocity = 60
        elif(radius < 70):
            velocity = 80
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

        for radius in radius_list:
            velocity = self.radius_to_velocity(radius)
            self.velocity_table.append(velocity)
        
        # Delay filter
        self.shift_velocity_table(5)

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

    def calc_error(self, line_sensor_val: list):
        # Similar to center of mass calculation
        num_half_sensors = int(8)
        count_left = 0
        count_right = 0
        sum_left = 0
        sum_right = 0
        for i in range (num_half_sensors):
            count_left += line_sensor_val[i]
            count_right += line_sensor_val[num_half_sensors + i]

            sum_left += i * line_sensor_val[num_half_sensors - 1 - i]
            sum_right += i * line_sensor_val[num_half_sensors + i]

        if count_left == 0:
            count_left = 1
        if count_right == 0:
            count_right = 1
        pos_left = sum_left / count_left
        pos_right = sum_right / count_right

        return (pos_left - pos_right)

    def run(self):
        time = 0
        finished = False
        last_dist_saved = 0
        vel_tbl_idx = 0
        self.create_velocity_table()
        self.base_speed = self.velocity_table[0]

        while not self.exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            dt = self.clock.get_time() / 1000
            if (not finished):
                time += dt 

            self.screen.fill((0, 0, 0))
            self.draw_map()
            self.draw_timer(time)


            line_sensor = self.robot.get_line_sensor(self.screen, self.screen_width, self.screen_height)

            # filter line
            if (line_sensor[0] or line_sensor[1] or line_sensor[14] or line_sensor[15]):
                if (line_sensor[7] == 1 or line_sensor[8] == 1 or line_sensor[6] == 1 or line_sensor[9] == 1):
                    line_sensor[0] = 0
                    line_sensor[1] = 0
                    line_sensor[15] = 0
                    line_sensor[14] = 0

            # print(line_sensor)
            error = self.calc_error(line_sensor)
            
            derivative = (error - self.last_error)
            l_speed = self.base_speed - (error * self.kp + derivative * self.kd)
            r_speed = self.base_speed + (error * self.kp + derivative * self.kd)
            self.robot.motor_l.set_voltage(l_speed)
            self.robot.motor_r.set_voltage(r_speed)
            
            self.last_error = error
            self.robot.update(dt)

            if (not finished):
                total_dist = float(self.robot.estimated_total_dist_cm)
                if (total_dist > (last_dist_saved + 10)):
                    vel_tbl_idx += 1
                    last_dist_saved = total_dist
                    
                    self.base_speed = self.velocity_table[vel_tbl_idx]
                    if (self.base_speed < 45):
                        self.kp = 6.5
                        self.kd = 2.5
                    else:
                        self.kp = 43
                        self.kd = 60
               



            # Count markers
            left_marker = line_sensor[16] == 1 or line_sensor[17] == 1
            right_marker = line_sensor[18] == 1 or line_sensor[19] == 1
            if (left_marker and not self.last_left_marker and not right_marker):
                self.left_marker_counter += 1
                print("Left marker - " + str(self.left_marker_counter))

            if (right_marker and not self.last_right_marker):
                self.right_marker_counter += 1
                print("Right marker - " + str(self.right_marker_counter))

                if (self.right_marker_counter == 1 and self.left_marker_counter < 2):
                    time = 0

                if (self.left_marker_counter > MIN_LEFT_MARKER_COUNTER):
                    print("Total time: " + str(round(time, 4)) + "s")
                    finished = True

                    self.base_speed = 15
                    self.kd = 0
                    self.kp = 0



            self.last_left_marker = left_marker
            self.last_right_marker = right_marker
            
            #Draw
            self.robot.display(self.screen)
            # self.robot.display_line_sensor(self.screen)
            pygame.display.flip()

            self.clock.tick(self.ticks)


            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()