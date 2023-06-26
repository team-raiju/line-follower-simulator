import pygame
from load_track import LoadMap
from robot import Robot
from helper import Helper as hp
from helper import PIDFunctions as pid
from helper import CountMarkers as cm

MAP_FILE_NAME = "map0.png"
MAP_WIDTH_CM = 100
MAP_HEIGHT_CM = 300
MAP_MARGIN_CM = 10
MAP_CM_PER_PIXELS = 2

ROBOT_INIT_POS_X_CM = 11
ROBOT_INIT_POS_Y_CM = 220
ROBOT_INIT_ANGLE = 90
MIN_LEFT_MARKER_COUNTER = 20

ROBOT_IMAGE = "robot-img.png"
ROBOT_SIZE_X_CM = 14.0  # Width
ROBOT_SIZE_Y_CM = 14.0  # Height
ROTATION_OFFSET_FROM_CENTER_CM = 4.73
WHEELS_DIST_CM = 14.0
WHEELS_RADIUS_CM = 1.0

INIT_BASE_SPEED = 100
INIT_KP = 35
INIT_KD = 70


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

        self.pid_calc = pid(INIT_BASE_SPEED, INIT_KP, INIT_KD)
    
    def run(self):
        time = 0
        finished = False

        count_markers = cm()

        while not self.exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            dt = self.clock.get_time() / 1000
            if not finished:
                time += dt

            self.screen.fill((0, 0, 0))
            self.map.draw_loaded_map()

            line_sensor = self.robot.get_line_sensor(self.screen, self.screen_width, self.screen_height)
            line_sensor = hp.filter_line(line_sensor, self.robot.white_val, self.robot.black_val)

            error = pid.calc_error(line_sensor, self.robot.line_sensor_pos[0:16])
            l_speed, r_speed = self.pid_calc.simple_pid(error)
            self.robot.set_motors_voltage(l_speed, r_speed)

            markers = count_markers.marker_process(line_sensor[16:18], line_sensor[18:20], 
                                         self.robot.white_val, self.robot.estimated_position_cm, self.robot.estimated_angle)

            if (markers["left_marker"]["seeing"]):
                self.left_marker_counter += 1
                print("Left marker - " + str(self.left_marker_counter))


            if (markers["right_marker"]["seeing"]):
                self.right_marker_counter += 1
                if self.right_marker_counter == 1 and self.left_marker_counter < 1:
                    print("Start")
                    time = 0

                elif self.left_marker_counter > MIN_LEFT_MARKER_COUNTER:
                    print("Total time: " + str(round(time, 4)) + "s")
                    finished = True
                    self.pid_calc = pid(15, 0, 0)

            self.robot.update(dt)

            hp.draw_timer(self.screen, time, MAP_CM_PER_PIXELS)
            self.robot.display(self.screen)
            pygame.display.flip()
            self.clock.tick(self.ticks)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
