import os
import pygame
from pygame.math import Vector2
from generate_track import Map
from robot import Robot

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Line Follower")
        self.screen_width = 560
        self.screen_height = 890
        self.screen = pygame.display.set_mode((self.screen_width , self.screen_height))
        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False
        self.last_error = 0

    def run(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "media" , "raiju.png")
        robot_image = pygame.image.load(image_path)

        robot = Robot(36, 200, 90)
        robot_size_x_cm = 12
        robot_size_y_cm = 6
        resized_image = pygame.transform.scale(robot_image, (robot.centimeters_to_pixel(robot_size_y_cm), robot.centimeters_to_pixel(robot_size_x_cm)))
        waypoint_idx = 0
        finished_counter = 0

        while not self.exit:
            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            dt = self.clock.get_time() / 1000

            # Line sensor
            line_sensor = robot.get_line_sensor(self.screen, self.screen_width, self.screen_height)
            # print(line_sensor)

            error = 1.5 * (line_sensor[7] - line_sensor[4]) + 3 * (line_sensor[9] - line_sensor[2]) + 2 * (line_sensor[8] -line_sensor[3]) + (line_sensor[6] - line_sensor[5])
            
            if (waypoint_idx >= 62):
                finished_counter += 1
                if (finished_counter > 50):
                    robot.motor_l.set_voltage(0)
                    robot.motor_r.set_voltage(0)
                else:
                    kp = 3.3
                    kd = 0.001
                    
                    derivative = kd * (error - self.last_error)
                    robot.motor_l.set_voltage(30 - (error * kp + derivative * kd))
                    robot.motor_r.set_voltage(30 + (error * kp + derivative * kd))

            elif (waypoint_idx < 37):
                kp = 5
                kd = 0.001
                
                derivative = kd * (error - self.last_error)
                robot.motor_l.set_voltage(41 - (error * kp + derivative * kd))
                robot.motor_r.set_voltage(41 + (error * kp + derivative * kd))
            elif waypoint_idx < 51:
                kp = 3.4
                kd = 0.001
                
                derivative = kd * (error - self.last_error)
                robot.motor_l.set_voltage(30 - (error * kp + derivative * kd))
                robot.motor_r.set_voltage(30 + (error * kp + derivative * kd))
            elif waypoint_idx < 61:
                kp = 7.2
                kd = 0.04
                
                derivative = kd * (error - self.last_error)
                robot.motor_l.set_voltage(27 - (error * kp + derivative * kd))
                robot.motor_r.set_voltage(27 + (error * kp + derivative * kd))

            else:
                kp = 5
                kd = 0.001
                derivative = kd * (error - self.last_error)
                robot.motor_l.set_voltage(42 - (error * kp + derivative * kd))
                robot.motor_r.set_voltage(42 + (error * kp + derivative * kd))


            self.last_error = error
            robot.update(dt)
            
            #Draw
            self.screen.fill((0, 0, 0))
            map = Map(20, 245, 270, self.screen)
            map.load_map_from_file()
            
            # Update travalled distance
            if (waypoint_idx < len(map.waypoint)):
                if (map.near_waypoint(robot.position, map.waypoint[waypoint_idx])):
                    waypoint_idx += 1
                    print(waypoint_idx)

            # Draw line sensor
            for sensor in robot.line_sensor_pos:
                sensor_position = robot.position + robot.centimeters_to_pixel(sensor).rotate(-robot.angle)
                line_sensor_draw = sensor_position + Vector2(3, 0).rotate(-robot.angle)
                pygame.draw.circle(self.screen, (255, 0, 255), (line_sensor_draw.x, line_sensor_draw.y), 1)


            rotated = pygame.transform.rotate(resized_image, robot.angle)
            rect = rotated.get_rect()
            self.screen.blit(rotated, robot.position- (rect.width / 2, rect.height / 2))
            pygame.display.flip()
            self.clock.tick(self.ticks)


            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()