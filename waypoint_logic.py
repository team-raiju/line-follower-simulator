import os
import pygame
from pygame.math import Vector2
from generate_track import Map
from robot import Robot
import math

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Line Follower")
        self.screen_width = 1280
        self.screen_height = 810
        self.screen = pygame.display.set_mode((self.screen_width , self.screen_height))
        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False
        self.last_error = 0
        self.robot = Robot(20, 245, 90)
    
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

    def run(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "raiju.png")
        robot_image = pygame.image.load(image_path)

        
        robot_size_x_cm = 12
        robot_size_y_cm = 6
        resized_image = pygame.transform.scale(robot_image, (self.robot.centimeters_to_pixel(robot_size_y_cm), self.robot.centimeters_to_pixel(robot_size_x_cm)))
        waypoint_idx = 0
        finished_counter = 0

        while not self.exit:
            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            dt = self.clock.get_time() / 1000
            
            #Draw
            self.screen.fill((0, 0, 0))
            map = Map(20, 245, 270, self.screen)
            map.gen_default_track()

            if (len(map.waypoint) > waypoint_idx):
                (dist, angleDiff) = self.trackGoal(self.robot.position, map.waypoint[waypoint_idx], self.robot.angle)

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
            if (waypoint_idx < len(map.waypoint)):
                if (map.near_waypoint(self.robot.position, waypoint_idx)):
                    waypoint_idx += 1
                    print(waypoint_idx)

            # print("")
            # print(map.waypoint[1])
            # print(self.robot.position)
        

            rotated = pygame.transform.rotate(resized_image, self.robot.angle)
            rect = rotated.get_rect()
            self.screen.blit(rotated, self.robot.position- (rect.width / 2, rect.height / 2))
            pygame.display.flip()
            self.clock.tick(self.ticks)


            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()