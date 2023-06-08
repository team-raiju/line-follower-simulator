import os
import pygame
from pygame.math import Vector2
from generate_track import Map
from load_track import LoadMap
from robot import Robot
import math

MAP_FILE_NAME = "map1.png"
MAP_WIDTH_CM = 230
MAP_HEIGHT_CM = 395
MAP_MARGIN_CM = 25
MAP_CM_PER_PIXELS = 2

ROBOT_SIZE_X_CM = 12
ROBOT_SIZE_Y_CM = 6
ROBOT_INIT_POS_X_CM = 36 
ROBOT_INIT_POS_Y_CM = 150
ROBOT_INIT_ANGLE = 90

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
        self.ticks = 60
        self.exit = False
        self.last_error = 0

        current_dir = os.path.dirname(os.path.abspath(__file__))
        robot_image_path = os.path.join(current_dir, "media" , "raiju.png")
        robot_image = pygame.image.load(robot_image_path)

        self.robot = Robot(MAP_CM_PER_PIXELS, ROBOT_INIT_POS_X_CM, ROBOT_INIT_POS_Y_CM, ROBOT_INIT_ANGLE)
        self.resized_robot_img = pygame.transform.scale(robot_image, (self.robot.centimeters_to_pixel(ROBOT_SIZE_Y_CM), self.robot.centimeters_to_pixel(ROBOT_SIZE_X_CM)))

        self.map = LoadMap(self.screen)
        self.map.load_map_from_file(MAP_FILE_NAME, margin_pixels, self.map_width_pixels, self.map_height_pixels)

        self.load_waypoint_list()

    def load_waypoint_list(self):

        self.waypoint_list = []
        current_dir = os.path.dirname(os.path.abspath(__file__))
        waypoint_list_path = os.path.join(current_dir, "image_conversion", "waypoints", "waypoints_map1.txt")

        with open(waypoint_list_path, "r") as f:
            for line in f:
                x, y = line.strip().split(",")
                point = Vector2(int(x), int(y))
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
    
    def set_motors_voltage(self, vel, w):
        self.robot.motor_l.set_voltage((2*vel - w) / 2) # w*d actually
        self.robot.motor_r.set_voltage((2*vel + w) / 2) # w*d actually

    def draw_robot(self):
        rotated = pygame.transform.rotate(self.resized_robot_img, self.robot.angle)
        rect = rotated.get_rect()
        self.screen.blit(rotated, self.robot.position - (rect.width / 2, rect.height / 2))

    def draw_map(self):
        self.map.draw_loaded_map()

    def run(self):
        waypoint_idx = 0

        while not self.exit:
            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            dt = self.clock.get_time() / 1000
            
            #Draw
            self.screen.fill((0, 0, 0))
            self.draw_map()

            if (len(self.waypoint_list) > waypoint_idx):
                (dist, angleDiff) = self.trackGoal(self.robot.position, self.waypoint_list[waypoint_idx], self.robot.angle)

                vel = 50
                w = -angleDiff * 0.35
                # print(angleDiff)

                self.set_motors_voltage(vel, w)
            else:
                (dist, angleDiff) = self.trackGoal(self.robot.position, Vector2(20, 320), self.robot.angle)
                if dist < 0:
                    dist = 0
                self.robot.motor_l.set_voltage(dist/5)
                self.robot.motor_r.set_voltage(dist/5)


            self.robot.update(dt)

            # Update travalled distance
            if (waypoint_idx < len(self.waypoint_list)):
                if (self.near_waypoint(self.robot.position, self.waypoint_list[waypoint_idx])):
                    waypoint_idx += 1
                    print(waypoint_idx)

            # print("")
            # print(self.waypoint_list[1])
            # print(self.robot.position)

            self.draw_robot()

            pygame.display.flip()
            self.clock.tick(self.ticks)


            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()