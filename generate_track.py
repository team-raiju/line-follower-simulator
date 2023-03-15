import pygame
import math
import random
from pygame.math import Vector2


class Map:
    def __init__(self, x, y, angle, screen):
        self.last_point = Vector2(x, y)
        self.last_angle = angle
        self.screen = screen
        self.line_color = (255, 255, 255)
        self.line_width = 6
        
    def gen_line(self, lenght):
        point1 = self.last_point + Vector2((self.line_width / 2), 0.0).rotate(self.last_angle + 90)
        point2 = self.last_point + Vector2((self.line_width / 2), 0.0).rotate(self.last_angle - 90)

        new_point = self.last_point + Vector2(lenght, 0.0).rotate(self.last_angle)
        point3 = new_point + Vector2((self.line_width / 2), 0.0).rotate(self.last_angle - 90)
        point4 = new_point + Vector2((self.line_width / 2), 0.0).rotate(self.last_angle + 90)

        pygame.draw.polygon(self.screen, self.line_color, (point1, point2, point3, point4))
        self.last_point = new_point

        # pygame.draw.circle(self.screen, (255, 0, 255), (point1.x,point1.y), 2)
        # pygame.draw.circle(self.screen, (255, 0, 255), (point2.x,point2.y), 2)
        # pygame.draw.circle(self.screen, (255, 0, 255), (point3.x,point3.y), 2)
        # pygame.draw.circle(self.screen, (255, 0, 255), (point4.x,point4.y), 2)
        

    def gen_arc_right(self, radius, arc_angle):
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


    def gen_arc_left(self, radius, arc_angle):
        scale_vector = Vector2(radius, 0.0)
        circle_center = self.last_point + scale_vector.rotate(self.last_angle - 90)

        radius_adjusted = radius + self.line_width / 2
        arc_init_angle = 270 - (self.last_angle) # Convert to angles accepeted by arc function

        pygame.draw.arc(self.screen, self.line_color, 
                        (circle_center.x - radius_adjusted, circle_center.y - radius_adjusted , (2 * radius_adjusted), (2 * radius_adjusted)),
                        math.radians(arc_init_angle), math.radians(arc_init_angle + arc_angle), self.line_width)
        

        self.gen_marker('Left', self.last_point)

        #Update position
        self.last_point += Vector2((2 * radius) * math.sin(math.radians(arc_angle/2)), 0.0).rotate(self.last_angle - arc_angle/2)
        self.last_angle -= arc_angle

        self.gen_marker('Left', self.last_point)


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
        # pygame.draw.line(self.screen, self.line_color, (marker_1_start.x, marker_1_start.y), (marker_1_end.x, marker_1_end.y), self.line_width)

        point1 = marker_1_start + Vector2((self.line_width / 2), 0.0).rotate(angle_to_rotate + 90)
        point2 = marker_1_start + Vector2((self.line_width / 2), 0.0).rotate(angle_to_rotate - 90)
        point3 = marker_1_end + Vector2((self.line_width / 2), 0.0).rotate(angle_to_rotate - 90)
        point4 = marker_1_end + Vector2((self.line_width / 2), 0.0).rotate(angle_to_rotate + 90)

        pygame.draw.polygon(self.screen, self.line_color, (point1, point2, point3, point4))



def main():
    # Initialize Pygame
    pygame.init()

    # Set up the display window
    screen = pygame.display.set_mode((1280, 720))

    map = Map(100, 500, 270, screen)

    map.gen_line(80)
    map.gen_marker('Right', map.last_point)
    map.gen_marker('Right', map.last_point + Vector2(100 , 0.0).rotate(map.last_angle))
    map.gen_line(260)


    map.gen_arc_right(30, 90)
    
    map.gen_line(420)

    map.gen_arc_right(100, 20)
    map.gen_arc_left(120, 40)
    map.gen_arc_right(100, 20)

    map.gen_line(420)

    map.gen_arc_right(80, 180)
    map.gen_arc_right(20, 90)
    map.gen_arc_left(80, 265)

    map.gen_line(100)

    map.gen_arc_right(50, 180)

    map.gen_line(600)

    map.gen_arc_left(20, 80)

    map.gen_line(115)

    map.gen_arc_left(80, 90)
    map.gen_arc_left(900, 40)
    map.gen_arc_left(20, 180)
    map.gen_arc_right(70, 50)
    map.gen_arc_left(70, 50)
    map.gen_arc_right(70, 50)
    map.gen_arc_left(70, 50)
    map.gen_arc_right(70, 50)
    map.gen_arc_left(70, 50)
    map.gen_arc_right(70, 50)
    map.gen_arc_left(70, 50)
    map.gen_arc_right(70, 125)

    map.gen_line(220)

    map.gen_arc_right(20, 180)
    map.gen_line(70)
    map.gen_arc_left(20, 180)
    map.gen_line(70)

    map.gen_arc_right(30, 100)
    map.gen_arc_left(60, 40)
    map.gen_arc_right(60, 90)
    map.gen_arc_right(20, 115)


    map.gen_line(400)

    map.gen_arc_left(100, 90)
    map.gen_arc_left(20, 90)
    map.gen_arc_right(50, 85)

    map.gen_line(170)

    map.gen_arc_right(80, 90)
    map.gen_arc_right(20, 200)
    map.gen_arc_left(20, 250)
    map.gen_arc_right(20, 125)

    map.gen_arc_left(20, 210)
    map.gen_arc_right(20, 210)
    map.gen_arc_left(20, 75)


    map.gen_line(25)

    map.gen_arc_right(20, 90)

    map.gen_line(105)


    # Update the display
    pygame.display.update()

    # Run the game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()



if __name__ == '__main__':
    main()