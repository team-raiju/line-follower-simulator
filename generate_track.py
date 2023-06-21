import pygame
import math
import random
from pygame.math import Vector2
import os

MAP_WIDTH_CM = 100
MAP_HEIGHT_CM = 300
MAP_MARGIN_CM = 0
MAP_CM_PER_PIXELS = 2

DRAW_INIT_POS_X_CM = 14
DRAW_INIT_POS_Y_CM = 224
DRAW_INIT_ANGLE = 270

class Map:
    def __init__(self, screen, cm_per_pixel):
        self.cm_per_pixel = cm_per_pixel
        self.last_point = Vector2(0, 0)
        self.last_angle = 0
        self.screen = screen
        self.line_color = (255, 255, 255)
        self.line_width = self.centimeters_to_pixel(2)

        self.waypoint = [self.last_point]
    
    def centimeters_to_pixel(self, centimeters):
        return centimeters * self.cm_per_pixel
        
    def gen_line(self, lenght_cm):
        lenght = self.centimeters_to_pixel(lenght_cm)
        point1 = self.last_point + Vector2((self.line_width / 2), 0.0).rotate(self.last_angle + 90)
        point2 = self.last_point + Vector2((self.line_width / 2), 0.0).rotate(self.last_angle - 90)

        new_point = self.last_point + Vector2(lenght, 0.0).rotate(self.last_angle)
        point3 = new_point + Vector2((self.line_width / 2), 0.0).rotate(self.last_angle - 90)
        point4 = new_point + Vector2((self.line_width / 2), 0.0).rotate(self.last_angle + 90)

        pygame.draw.polygon(self.screen, self.line_color, (point1, point2, point3, point4))
        self.last_point = new_point
        self.waypoint.append(new_point.copy())

        # pygame.draw.circle(self.screen, (255, 0, 255), (point1.x,point1.y), 2)
        # pygame.draw.circle(self.screen, (255, 0, 255), (point2.x,point2.y), 2)
        # pygame.draw.circle(self.screen, (255, 0, 255), (point3.x,point3.y), 2)
        # pygame.draw.circle(self.screen, (255, 0, 255), (point4.x,point4.y), 2)
        

    def gen_arc_right(self, radius_cm, arc_angle):
        radius = self.centimeters_to_pixel(radius_cm)
        scale_vector = Vector2(radius, 0.0)
        circle_center = self.last_point + scale_vector.rotate(self.last_angle + 90)

        radius_adjusted = radius + self.line_width / 2
        arc_final_angle = 360 - (self.last_angle - 90) # Convert to angles accepeted by arc function

        pygame.draw.arc(self.screen, self.line_color, 
                        (circle_center.x - radius_adjusted, circle_center.y - radius_adjusted , (2 * radius_adjusted), (2 * radius_adjusted)),
                        math.radians(arc_final_angle - arc_angle), math.radians(arc_final_angle), self.line_width)
        
        # Draw end side line
        self.gen_marker('Left', self.last_point)
        
        #Update position
        self.last_point += Vector2((2 * radius) * math.sin(math.radians(arc_angle/2)), 0.0).rotate(self.last_angle + arc_angle/2)
        self.last_angle += arc_angle

        # Draw end side line
        self.gen_marker('Left', self.last_point)
        self.waypoint.append(self.last_point.copy())



    def gen_arc_left(self, radius_cm, arc_angle):
        radius = self.centimeters_to_pixel(radius_cm)
        scale_vector = Vector2(radius, 0.0)
        circle_center = self.last_point + scale_vector.rotate(self.last_angle - 90)

        radius_adjusted = radius + self.line_width / 2

        # Convert to angles accepeted by arc function
        arc_init_angle = 270 - (self.last_angle) 

        pygame.draw.arc(self.screen, self.line_color, 
                        (circle_center.x - radius_adjusted, circle_center.y - radius_adjusted , (2 * radius_adjusted), (2 * radius_adjusted)),
                        math.radians(arc_init_angle), math.radians(arc_init_angle + arc_angle), self.line_width)
        

        self.gen_marker('Left', self.last_point)

        #Update position
        self.last_point += Vector2((2 * radius) * math.sin(math.radians(arc_angle/2)), 0.0).rotate(self.last_angle - arc_angle/2)
        self.last_angle -= arc_angle

        self.gen_marker('Left', self.last_point)

        self.waypoint.append(self.last_point.copy())

        # pygame.draw.circle(self.screen, (255, 0, 255), (self.last_point.x,self.last_point.y), 2)

    def gen_marker(self, side, point: Vector2):
        marker_start_distance = 2 * self.line_width + (self.line_width/2)
        marker_end_distance = 4 * self.line_width + (self.line_width/2)

        angle_to_rotate = 0
        if side == 'Right':
            angle_to_rotate = self.last_angle + 90
        else:
            angle_to_rotate = self.last_angle - 90

        marker_1_start = point + Vector2(marker_start_distance, 0.0).rotate(angle_to_rotate)
        marker_1_end = point + Vector2(marker_end_distance, 0.0).rotate(angle_to_rotate)

        point1 = marker_1_start + Vector2((self.line_width / 2), 0.0).rotate(angle_to_rotate + 90)
        point2 = marker_1_start + Vector2((self.line_width / 2), 0.0).rotate(angle_to_rotate - 90)
        point3 = marker_1_end + Vector2((self.line_width / 2), 0.0).rotate(angle_to_rotate - 90)
        point4 = marker_1_end + Vector2((self.line_width / 2), 0.0).rotate(angle_to_rotate + 90)

        pygame.draw.polygon(self.screen, self.line_color, (point1, point2, point3, point4))
    
    def near_waypoint(self, point: Vector2, point_2: Vector2):
        distance = point.distance_to(point_2)
        max_dist_cm = 15
        if (abs(distance) < self.centimeters_to_pixel(max_dist_cm)):
            return True
        return False

    def gen_default_track(self, x_cm, y_cm, angle ):
        x = self.centimeters_to_pixel(x_cm)
        y = self.centimeters_to_pixel(y_cm)
        self.last_point = Vector2(x, y)
        self.last_angle = angle
    
        self.gen_marker('Right', self.last_point)
        self.gen_line(60)
        self.gen_marker('Right', self.last_point)
        self.gen_line(140)

        
        self.gen_arc_right(15,180)

        self.gen_line(20)

        self.gen_arc_left(15,180)

        self.gen_line(20)

        self.gen_arc_right(10,270)

        self.gen_line(47)

        self.gen_arc_left(10,120)

        self.gen_line(40)

        self.gen_arc_right(15,90)

        self.gen_arc_left(15,105)

        self.gen_arc_right(15,90)

        self.gen_arc_left(15,105)

        self.gen_arc_right(15,90)

        self.gen_arc_left(15,30)


        self.gen_line(50)

        self.gen_arc_left(10,180)

        self.gen_line(150)

        self.gen_arc_right(10,180)

        self.gen_line(158)

        self.gen_arc_right(30,90)

        self.gen_line(32)

        self.gen_arc_right(10,90)

        self.gen_line(54)





def main():
    # Initialize Pygame
    pygame.init()

    map_width_pixels = MAP_WIDTH_CM * MAP_CM_PER_PIXELS
    map_height_pixels = MAP_HEIGHT_CM * MAP_CM_PER_PIXELS
    margin_pixels = MAP_MARGIN_CM * MAP_CM_PER_PIXELS

    screen_width = map_width_pixels + (2 * margin_pixels)
    screen_height = map_height_pixels + (2 * margin_pixels)


    # Set up the display window
    screen = pygame.display.set_mode((screen_width, screen_height))
    map = Map(screen, MAP_CM_PER_PIXELS)
    map.gen_default_track(DRAW_INIT_POS_X_CM, DRAW_INIT_POS_Y_CM, DRAW_INIT_ANGLE)

    pygame.image.save(screen, "image.png")

    # Update the display
    pygame.display.update()

    # Run the game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()



if __name__ == '__main__':
    main()