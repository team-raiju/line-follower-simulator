import pygame
import math
import random
from pygame.math import Vector2


# Initialize Pygame
pygame.init()

# Set up the display window
screen = pygame.display.set_mode((1280, 720))

# Set the line color
line_color = (255, 255, 255)

# Set the corner radius
corner_radius = 20

# Calculate the rectangle dimensions
rect_width = 200
rect_height = 100

# Calculate the rectangle position
rect_x = (800 - rect_width) // 2
rect_y = (600 - rect_height) // 2

# Draw the rectangle with rounded corners
last_angle = 180
last_point = Vector2(300, 500)
pygame.draw.line(screen, line_color, (600,500), (last_point.x, last_point.y), width=6)


for i in range(0, 2):
    is_line = random.randint(0,1)
    is_line = 0

    if(is_line == 1):
        lenght = random.randint(20,100)
        scale_vector = Vector2(lenght, 0.0)
        new_point = last_point + scale_vector.rotate(last_angle)
        # last_angle += 30
        pygame.draw.line(screen, line_color, (last_point.x, last_point.y), (new_point.x, new_point.y), width=6)
    else:
        radius = random.randint(40,100) 
        angle = random.randint(45, 180)
        scale_vector = Vector2(2 * radius, 0.0)
        circle_center = last_point + scale_vector.rotate(270) * 0.5

        print(angle)
        # print(radius)

        pygame.draw.arc(screen, line_color, (circle_center.x - radius + 0, circle_center.y - radius + 3, 2 * radius, 2 * radius), math.radians(270-angle), math.radians(270), 6)
        last_angle += angle
        new_point = last_point + scale_vector.rotate(last_angle)
        print(last_angle)


    last_point = new_point


# Update the display
pygame.display.update()

# Run the game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
