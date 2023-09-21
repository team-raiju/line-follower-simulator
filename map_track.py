import os
import pygame
from pygame.math import Vector2
from load_track import LoadMap
from robot import Robot
import math
from helper import Helper as hp
from helper import PIDFunctions as pid
from helper import CountMarkers as cm

MAPPING_NAME = "map2"

MAP_FILE_NAME = "map2.png"
MAP_WIDTH_CM = 186
MAP_HEIGHT_CM = 354
MAP_MARGIN_CM = 25
MAP_CM_PER_PIXELS = 2

ROBOT_INIT_POS_X_CM = 178 
ROBOT_INIT_POS_Y_CM = 75
ROBOT_INIT_ANGLE = 270
MIN_LEFT_MARKER_COUNTER = 15

ROBOT_IMAGE = "robot-img-3.png"
ROBOT_SIZE_X_CM = 18.0 # Width
ROBOT_SIZE_Y_CM = 15.0 # Height
ROTATION_OFFSET_FROM_CENTER_CM = 3.72
WHEELS_DIST_CM = 12.0
WHEELS_RADIUS_CM = 1.0

INIT_BASE_SPEED = 80
INIT_KP = 43
INIT_KD = 60

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

        self.last_dist_saved = 0
        self.last_theta = 0

        self.left_marker_counter = 0
        self.right_marker_counter = 0

        self.pid_calc = pid(INIT_BASE_SPEED, INIT_KP, INIT_KD)

        self.track_points = []
        self.track_points_new = []
        self.track_points_real = []
        self.track_markers = []
        self.track_markers_center = []
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


        file_path = os.path.join(current_dir, "maps", "mapping_data", MAPPING_NAME, (MAPPING_NAME + "_track_new.txt"))
        with open(file_path, "w") as f:
            for point in self.track_points_new:
                f.write(f"{point[0]},{point[1]}\n")
        

        file_path = os.path.join(current_dir, "maps", "mapping_data", MAPPING_NAME, (MAPPING_NAME + "_track_real.txt"))
        with open(file_path, "w") as f:
            for point in self.track_points_real:
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
        
        file_path = os.path.join(current_dir, "maps", "mapping_data", MAPPING_NAME, (MAPPING_NAME + "_markers.txt"))
        with open(file_path, "w") as f:
            for marker in self.track_markers:
                f.write(f"{marker[0]},{marker[1]}\n")


    def gen_waypoint(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "maps", "mapping_data", MAPPING_NAME, (MAPPING_NAME + "_waypoints.txt"))

        # check for circles and add waypoints right before and in the middle of circles
        with open(file_path, "w") as f:
            for i in range(len(self.radius_list)):
                if (abs(self.radius_list[i]) < 150):
                    point = self.track_points[i]
                    f.write(f"{point[0]},{point[1]}\n")
        
            # Always write the last point
            point = self.track_points[-1]
            f.write(f"{point[0]},{point[1]}\n")



    def gen_optimized_waypoints(self):
        centers = []
        optimized_points = []

        for i in range(len(self.track_markers) - 1):
            circle_center_x = (self.track_markers[i].x + self.track_markers[i + 1].x) / 2
            circle_center_y = (self.track_markers[i].y  + self.track_markers[i + 1].y) / 2
            point = (circle_center_x, circle_center_y)
            center = Vector2(point[0], point[1])
            centers.append(center)
            # x_val_pixel, y_val_pixel = self.coord_cm_to_pixel(point)
            # pygame.draw.circle(self.screen, (255, 0, 0), (x_val_pixel, y_val_pixel), 3, 0)


        # 1. Get average curvature between markers
        # 2. If is circle, then try to generate shortcuts.
        for i in range(len(self.points_between_markers) - 1):
            init = self.points_between_markers[i]
            end  = self.points_between_markers[i + 1]
            num_of_points = max((end - init), 1)
            radius_sum = sum(self.radius_list[init: end])
            mean_radius = radius_sum / num_of_points

            marker_center = (self.track_markers_center[i].x, self.track_markers_center[i].y)
            optimized_points.append(marker_center)

            if (mean_radius < 4000):
                waypoints = []
                
                if (num_of_points <= 5 and num_of_points > 0):
                    waypoint = self.track_points[int((init + end) / 2)]
                    waypoints.append(waypoint)
                else:
                    for j in range((init + 2), end - 3, 2):
                        waypoint = self.track_points[int(j)]
                        waypoints.append(waypoint)

                for item in waypoints:
                    my_vect = Vector2(item[0], item[1])
                    dx = my_vect.x - centers[i].x
                    dy = my_vect.y - centers[i].y
                    angleDiffRaw = (math.atan2(dy, dx) * 180 / math.pi)

                    new_vect = my_vect - Vector2(10, 0).rotate(angleDiffRaw)
                    optimized_points.append(new_vect)

        # Save optimized points
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "maps", "mapping_data", MAPPING_NAME, (MAPPING_NAME + "_opt_waypoints.txt"))

        with open(file_path, "w") as f:
            for optimized in optimized_points:
                f.write(f"{optimized[0]},{optimized[1]}\n")
                x_val_pixel, y_val_pixel = hp.coord_cm_to_pixel(optimized, MAP_CM_PER_PIXELS, MAP_MARGIN_CM)
                pygame.draw.circle(self.screen, (0, 0, 255), (x_val_pixel, y_val_pixel), 3, 0)

             # Always write the last point
            point = self.track_points[-1]
            f.write(f"{point[0]},{point[1]}\n")


    def append_point(self):
        total_dist = float(self.robot.estimated_total_dist_cm)
        if (total_dist > (self.last_dist_saved + TRACK_POINTS_DIST_CM)):


            print(self.robot.kalman_pos)
            print(self.robot.position_real_position_cm)
            print("")

            offset = Vector2(self.robot.rot_center_offset_cm, 0)

            # Old method
            sensor_position = self.robot.estimated_position_cm + self.robot.line_sensor_pos[7].rotate(-self.robot.estimated_angle) + offset.rotate(-self.robot.estimated_angle)
            
            # Remove Margin to save absolute position
            sensor_position.x -= MAP_MARGIN_CM
            sensor_position.y -= MAP_MARGIN_CM
            self.track_points.append(sensor_position)

            # New method
            sensor_position_new = self.robot.estimated_position_cm_new + self.robot.line_sensor_pos[7].rotate(-self.robot.estimated_angle) + offset.rotate(-self.robot.estimated_angle)
            sensor_position_new.x -= MAP_MARGIN_CM
            sensor_position_new.y -= MAP_MARGIN_CM
            self.track_points_new.append(sensor_position_new)


            # Real Position
            sensor_position_real = self.robot.position_real_position_cm + self.robot.line_sensor_pos[7].rotate(-self.robot.estimated_angle) + offset.rotate(-self.robot.estimated_angle)
            sensor_position_real.x -= MAP_MARGIN_CM
            sensor_position_real.y -= MAP_MARGIN_CM
            self.track_points_real.append(sensor_position_real)


            self.track_total_dist.append(total_dist)
            self.track_thetas.append(float(self.robot.estimated_angle))

            delta_theta = self.robot.estimated_angle - self.last_theta
            radius = 5000
            if delta_theta != 0:
                theta_rad = math.radians(delta_theta)
                radius = (total_dist - self.last_dist_saved) / theta_rad
            
            # print(radius)
            self.radius_list.append(radius)

            self.last_dist_saved = total_dist
            self.last_theta = float(self.robot.estimated_angle)

    def run(self):
        time = 0
        finished = False
        count_markers = cm()

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


            line_sensor = self.robot.get_line_sensor(self.screen, self.screen_width, self.screen_height)
            line_sensor = hp.filter_line(line_sensor, self.robot.white_val, self.robot.black_val)

            error = pid.calc_error(line_sensor, self.robot.line_sensor_pos[0:16])
            if (error == -99):
                error = self.pid_calc.get_last_error()

            l_speed, r_speed = self.pid_calc.simple_pid(error)
            self.robot.set_motors_voltage(l_speed, r_speed)
            
            # Append point every 5 cm
            self.append_point()

            # Count markers
            markers = count_markers.marker_process(line_sensor[16:18], line_sensor[18:20], 
                                         self.robot.white_val, self.robot.estimated_position_cm, self.robot.estimated_angle)
            
            if (markers["left_marker"]["seeing"]):
                self.left_marker_counter += 1
                print("Left marker - " + str(self.left_marker_counter))
                marker_raw_pos: Vector2 = markers["left_marker"]["position"]
                marker_raw_angle = markers["left_marker"]["rotation"]

                offset = Vector2(self.robot.rot_center_offset_cm, 0)
                sensor_position = marker_raw_pos + self.robot.line_sensor_pos[16].rotate(-marker_raw_angle) + offset.rotate(-marker_raw_angle)
                sensor_position.x -= MAP_MARGIN_CM
                sensor_position.y -= MAP_MARGIN_CM
                self.track_markers.append(sensor_position)

                robot_center = Vector2(marker_raw_pos.x - MAP_MARGIN_CM, marker_raw_pos.y - MAP_MARGIN_CM)
                left_marker_position_center = robot_center
                self.track_markers_center.append(left_marker_position_center)

                self.points_between_markers.append(int(len(self.track_points)))


            if (markers["right_marker"]["seeing"]):
                self.right_marker_counter += 1
                print("Right marker - " + str(self.right_marker_counter))

                if (self.right_marker_counter == 1 and self.left_marker_counter < 1):
                    print("Start")
                    time = 0

                elif (self.left_marker_counter > MIN_LEFT_MARKER_COUNTER):
                    print("Total time: " + str(round(time, 4)) + "s")
                    self.save_track_mapped()
                    self.gen_waypoint()
                    self.gen_optimized_waypoints()
                    finished = True
                    self.pid_calc = pid(15, 0, 0)

            self.robot.update(dt)

            #Draw
            self.robot.display(self.screen)
            pygame.display.flip()
            self.clock.tick(self.ticks)


            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()