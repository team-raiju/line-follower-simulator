import os
import pygame
from pygame.math import Vector2
from generate_track import Map
from load_track import LoadMap
from robot import Robot
import math

MAPPING_NAME = "map0"

MAP_FILE_NAME = "map0.png"
MAP_WIDTH_CM = 100
MAP_HEIGHT_CM = 300
MAP_MARGIN_CM = 10
MAP_CM_PER_PIXELS = 3

ROBOT_INIT_POS_X_CM = 11
ROBOT_INIT_POS_Y_CM = 220
ROBOT_INIT_ANGLE = 90
MIN_LEFT_MARKER_COUNTER = 22

ROBOT_IMAGE = "robot-img.png"
ROBOT_SIZE_X_CM = 14.0 # Width
ROBOT_SIZE_Y_CM = 14.0 # Height
ROTATION_OFFSET_FROM_CENTER_CM = 4.73
WHEELS_DIST_CM = 14.0
WHEELS_RADIUS_CM = 1.0


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

        self.left_marker_counter = 0
        self.right_marker_counter = 0
        self.last_left_marker = False
        self.last_right_marker = False
        self.last_error = 0
        
        self.base_speed = 33
        self.kp = 5
        self.kd = 2.5

        self.track_points = []
        self.track_markers = []
        self.points_between_markers = []
        self.track_total_dist = []
        self.track_thetas = []
        self.radius_list = []

    
    def save_track_mapped(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "maps", "mapping_data", MAPPING_NAME, (MAPPING_NAME + "_track.txt"))

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            for point in self.track_points:
                f.write(f"{point[0]},{point[1]}\n")
        
        file_path = os.path.join(current_dir, "maps", "mapping_data", MAPPING_NAME, (MAPPING_NAME + "_total_dist.txt"))
        with open(file_path, "w") as f:
            for num in self.track_total_dist:
                f.write(f"{num}\n")


        file_path = os.path.join(current_dir, "maps", "mapping_data", MAPPING_NAME, (MAPPING_NAME + "_thetas.txt"))
        with open(file_path, "w") as f:
            for theta in self.track_thetas:
                f.write(f"{theta}\n")
        
        file_path = os.path.join(current_dir, "maps", "mapping_data", MAPPING_NAME, (MAPPING_NAME + "_radius.txt"))
        with open(file_path, "w") as f:
            for radius in self.radius_list:
                f.write(f"{radius}\n")


    def gen_waypoint(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "maps", "mapping_data", MAPPING_NAME, (MAPPING_NAME + "_waypoints.txt"))

        # check for circles and add waypoints right before and in the middle of circles
        with open(file_path, "w") as f:
            for i in range(len(self.radius_list)):
                if (self.radius_list[i] < 150):
                    point = self.track_points[i]
                    f.write(f"{point[0]},{point[1]}\n")


        

    # def gen_optimized_waypoints(self):
        

    
    def draw_map(self):
        self.map.draw_loaded_map()
    
    def draw_timer(self, time):
        text_surface = pygame.font.Font(None, 36).render("Time: " + "{:.3f}s".format(time), True, (255, 0, 0))
        self.screen.blit(text_surface, (10, 10))

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
    
    def filter_line(self, line_sensor: list):
        if (
            line_sensor[0] == self.robot.white_val
            or line_sensor[1] == self.robot.white_val
            or line_sensor[14] == self.robot.white_val
            or line_sensor[15] == self.robot.white_val
        ):
            if (
                line_sensor[7] == self.robot.white_val
                or line_sensor[8] == self.robot.white_val
                or line_sensor[6] == self.robot.white_val
                or line_sensor[9] == self.robot.white_val
            ):
                line_sensor[0] = self.robot.black_val
                line_sensor[1] = self.robot.black_val
                line_sensor[15] = self.robot.black_val
                line_sensor[14] = self.robot.black_val
        return line_sensor

    def run(self):
        time = 0
        finished = False
        last_dist_saved = 0
        last_theta = 0
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


            line_sensor = self.robot.get_line_sensor(
                self.screen, self.screen_width, self.screen_height
            )

            line_sensor = self.filter_line(line_sensor)

            error = self.calc_error(line_sensor)
            
            derivative = (error - self.last_error)
            l_speed = self.base_speed - (error * self.kp + derivative * self.kd)
            r_speed = self.base_speed + (error * self.kp + derivative * self.kd)
            self.robot.motor_l.set_voltage(l_speed)
            self.robot.motor_r.set_voltage(r_speed)
            
            self.last_error = error
            self.robot.update(dt)


            # Append point every 5 cm
            total_dist = float(self.robot.estimated_total_dist_cm)
            if (total_dist > (last_dist_saved + 5)):
                offset = Vector2(self.robot.rot_center_offset_cm, 0)
                sensor_position = self.robot.estimated_position_cm + self.robot.line_sensor_pos[7].rotate(-self.robot.estimated_angle) + offset.rotate(-self.robot.estimated_angle)
                
                # Remove Margin to save absolute position
                sensor_position.x -= MAP_MARGIN_CM
                sensor_position.y -= MAP_MARGIN_CM
                self.track_points.append(sensor_position)

                self.track_total_dist.append(total_dist)
                self.track_thetas.append(float(self.robot.estimated_angle))

                delta_theta = self.robot.estimated_angle - last_theta
                radius = 5000
                if delta_theta != 0:
                    theta_rad = math.radians(delta_theta)
                    radius = abs((total_dist - last_dist_saved) / theta_rad)
                
                print(radius)
                self.radius_list.append(radius)

                last_dist_saved = total_dist
                last_theta = float(self.robot.estimated_angle)

        
            # Count markers
            left_marker = line_sensor[16] == 1 or line_sensor[17] == 1
            right_marker = line_sensor[18] == 1 or line_sensor[19] == 1
            if (left_marker and not self.last_left_marker):
                self.left_marker_counter += 1
                print("Left marker - " + str(self.left_marker_counter))

                offset = Vector2(self.robot.rot_center_offset_cm, 0)
                sensor_position = self.robot.estimated_position_cm + self.robot.line_sensor_pos[0].rotate(-self.robot.estimated_angle) + offset.rotate(-self.robot.estimated_angle)
                self.track_markers.append(sensor_position)
                self.points_between_markers.append(int(len(self.track_points)))

            if (right_marker and not self.last_right_marker):
                self.right_marker_counter += 1
                print("Right marker - " + str(self.right_marker_counter))

                if (self.right_marker_counter == 1 and self.left_marker_counter < 2):
                    time = 0

                if (self.left_marker_counter > MIN_LEFT_MARKER_COUNTER):
                    print("Total time: " + str(round(time, 4)) + "s")
                    self.save_track_mapped()
                    self.gen_waypoint()
                    # self.gen_optimized_waypoints()
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