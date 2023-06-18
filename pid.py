import os
import pygame
from pygame.math import Vector2
from generate_track import Map
from load_track import LoadMap
from robot import Robot

MAP_FILE_NAME = "map6.png"
MAP_WIDTH_CM = 303
MAP_HEIGHT_CM = 227
MAP_MARGIN_CM = 25
MAP_CM_PER_PIXELS = 3

ROBOT_INIT_POS_X_CM = 34
ROBOT_INIT_POS_Y_CM = 160
ROBOT_INIT_ANGLE = 90
MIN_LEFT_MARKER_COUNTER = 54

ROBOT_IMAGE = "robot-img.png"
ROBOT_SIZE_X_CM = 14.0  # Width
ROBOT_SIZE_Y_CM = 14.0  # Height
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
            ROBOT_INIT_POS_X_CM,
            ROBOT_INIT_POS_Y_CM,
            ROBOT_INIT_ANGLE,
            ROBOT_IMAGE,
        )

        self.map = LoadMap(self.screen)
        self.map.load_map_from_file(
            MAP_FILE_NAME, margin_pixels, self.map_width_pixels, self.map_height_pixels
        )

        self.left_marker_counter = 0
        self.right_marker_counter = 0
        self.last_left_marker = False
        self.last_right_marker = False
        self.last_error = 0

        self.base_speed = 100
        self.kp = 43
        self.kd = 60

        self.kp_w = 7
        self.kd_w = 10

    def draw_map(self):
        self.map.draw_loaded_map()

    def draw_timer(self, time):
        text_surface = pygame.font.Font(None, 36).render(
            "Time: " + "{:.3f}s".format(time), True, (255, 0, 0)
        )
        self.screen.blit(text_surface, (10, 10))

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

    def count_markers(self, line_sensor: list):
        right_counter_increased = False
        left_marker = (
            line_sensor[16] == self.robot.white_val
            or line_sensor[17] == self.robot.white_val
        )
        right_marker = (
            line_sensor[18] == self.robot.white_val
            or line_sensor[19] == self.robot.white_val
        )
        if left_marker and not self.last_left_marker:
            self.left_marker_counter += 1
            print("Left marker - " + str(self.left_marker_counter))
        if right_marker and not self.last_right_marker:
            self.right_marker_counter += 1
            print("Right marker - " + str(self.right_marker_counter))
            right_counter_increased = True
        self.last_left_marker = left_marker
        self.last_right_marker = right_marker
        return right_counter_increased

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
        l_speed = self.base_speed - (error * self.kp + derivative * self.kd)
        r_speed = self.base_speed + (error * self.kp + derivative * self.kd)
        self.last_error = error

        return l_speed, r_speed
    
    def process_angle_pid(self, line_sensor_values: list):
        omega_error = self.calc_error(line_sensor_values)

        derivative = (omega_error - self.last_error)
        w = (omega_error * self.kp_w + derivative * self.kd_w)

        self.last_error = omega_error
        return w



    def run(self):
        time = 0
        finished = False
        while not self.exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            dt = self.clock.get_time() / 1000
            if not finished:
                time += dt

            self.screen.fill((0, 0, 0))
            self.draw_map()
            self.draw_timer(time)

            line_sensor = self.robot.get_line_sensor(
                self.screen, self.screen_width, self.screen_height
            )
            line_sensor = self.filter_line(line_sensor)

            # l_speed, r_speed = self.process_simple_pid(line_sensor)
            # self.robot.set_motors_voltage(l_speed, r_speed)

            w = self.process_angle_pid(line_sensor)
            self.robot.set_motors_voltage_vel_w(self.base_speed, w)

            self.robot.update(dt)

            right_counter_changed = self.count_markers(line_sensor)

            if right_counter_changed:
                if self.right_marker_counter == 1 and self.left_marker_counter < 1:
                    time = 0

                elif self.left_marker_counter > MIN_LEFT_MARKER_COUNTER:
                    print("Total time: " + str(round(time, 4)) + "s")
                    finished = True

                    self.base_speed = 15
                    self.kd = self.kp = self.kp_w = self.kd_w = 0

            self.robot.display(self.screen)
            pygame.display.flip()

            self.clock.tick(self.ticks)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
