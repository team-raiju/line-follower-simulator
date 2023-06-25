import os
import pygame
from pygame.math import Vector2
from generate_track import Map
from load_track import LoadMap
from robot import Robot
import math

MAPPING_NAME = "map3"

MAP_FILE_NAME = "map3.png"
MAP_WIDTH_CM = 545
MAP_HEIGHT_CM = 595
MAP_MARGIN_CM = 25
MAP_CM_PER_PIXELS = 1.5

ROBOT_INIT_POS_X_CM = 175
ROBOT_INIT_POS_Y_CM = 12
ROBOT_INIT_ANGLE = 180
MIN_LEFT_MARKER_COUNTER = 40

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
        self.kp = 3
        self.kd = 1.5

        self.track_points = []
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
                f.write(f"{marker}\n")


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
        optmized_points = []

        for i in range(len(self.track_markers) - 1):
            circle_center_x = (self.track_markers[i][0] + self.track_markers[i + 1][0]) / 2
            circle_center_y = (self.track_markers[i][1]  + self.track_markers[i + 1][1]) / 2
            point = (circle_center_x, circle_center_y)
            # x_val_pixel, y_val_pixel = self.coord_cm_to_pixel(point)
            center = Vector2(point[0], point[1])
            centers.append(center)
            # pygame.draw.circle(self.screen, (255, 0, 0), (x_val_pixel, y_val_pixel), 3, 0)


        # get medium curvature between markers
        # If circle, then aproxima o centro do centro. E a cada 2 para o lado aproxima do centro tambem
        for i in range(len(self.points_between_markers) - 1):
            init = self.points_between_markers[i]
            end  = self.points_between_markers[i + 1]
            num_of_points = max((end - init), 1)
            radius_sum = sum(self.radius_list[init: end])
            mean_radius = radius_sum / num_of_points

            marker_center = (self.track_markers_center[i][0], self.track_markers_center[i][1])
            optmized_points.append(marker_center)

            if (mean_radius < 1000):
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
                    optmized_points.append(new_vect)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "maps", "mapping_data", MAPPING_NAME, (MAPPING_NAME + "_opt_waypoints.txt"))

        with open(file_path, "w") as f:
            for optmized in optmized_points:
                f.write(f"{optmized[0]},{optmized[1]}\n")
                x_val_pixel, y_val_pixel = self.coord_cm_to_pixel(optmized)
                pygame.draw.circle(self.screen, (0, 0, 255), (x_val_pixel, y_val_pixel), 3, 0)

             # Always write the last point
            point = self.track_points[-1]
            f.write(f"{point[0]},{point[1]}\n")


    def coord_cm_to_pixel(self, point):
        x_val_pixel = (point[0] + MAP_MARGIN_CM) * MAP_CM_PER_PIXELS
        y_val_pixel = (point[1] + MAP_MARGIN_CM) * MAP_CM_PER_PIXELS
        return x_val_pixel, y_val_pixel
    
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

        start_left_marker = False
        left_marker_position = Vector2(0, 0)
        left_marker_position_center = Vector2(0, 0)

        start_right_marker = False

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
                    radius = (total_dist - last_dist_saved) / theta_rad
                
                print(radius)
                self.radius_list.append(radius)

                last_dist_saved = total_dist
                last_theta = float(self.robot.estimated_angle)

        
            # Count markers
            left_marker = line_sensor[16] == 1 or line_sensor[17] == 1
            right_marker = line_sensor[18] == 1 or line_sensor[19] == 1
            
            if (start_left_marker):
                if (right_marker):
                    start_left_marker = False
                    print("Crossing L")
                elif (not left_marker and self.last_left_marker):
                    self.left_marker_counter += 1
                    print("Left marker - " + str(self.left_marker_counter))
                    self.track_markers.append(left_marker_position)
                    self.track_markers_center.append(left_marker_position_center)
                    self.points_between_markers.append(int(len(self.track_points)))
                    start_left_marker = False

            else:
                if (left_marker and not self.last_left_marker and not right_marker):
                    start_left_marker = True
                    offset = Vector2(self.robot.rot_center_offset_cm, 0)
                    sensor_position = self.robot.estimated_position_cm + self.robot.line_sensor_pos[16].rotate(-self.robot.estimated_angle) + offset.rotate(-self.robot.estimated_angle)
                    sensor_position.x -= MAP_MARGIN_CM
                    sensor_position.y -= MAP_MARGIN_CM
                    left_marker_position = sensor_position

                    # Center of the robot
                    robot_center = Vector2(self.robot.estimated_position_cm.x, self.robot.estimated_position_cm.y)
                    robot_center.x -= MAP_MARGIN_CM
                    robot_center.y -= MAP_MARGIN_CM
                    left_marker_position_center = robot_center



            if (start_right_marker):
                if (left_marker):
                    start_right_marker = False
                    print("Crossing R")
                elif (not right_marker and self.last_right_marker):
                    self.right_marker_counter += 1
                    print("Right marker - " + str(self.right_marker_counter))

                    if (self.right_marker_counter == 1 and self.left_marker_counter < 2):
                        time = 0

                    if (self.left_marker_counter > MIN_LEFT_MARKER_COUNTER):
                        print("Total time: " + str(round(time, 4)) + "s")
                        self.save_track_mapped()
                        self.gen_waypoint()
                        self.gen_optimized_waypoints()
                        finished = True

                        self.base_speed = 15
                        self.kd = 0
                        self.kp = 0
                    
                    start_right_marker = False

            else:
                if (right_marker and not self.last_right_marker and not left_marker):
                    start_right_marker = True


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