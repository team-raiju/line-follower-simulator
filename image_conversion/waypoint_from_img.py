import os
import pygame
from pygame.math import Vector2
import math

INPUT_MAP_NAME = "map0.png"
WAYPOINT_LIST_NAME = "waypoints_map0-9.txt"

MAP_WIDTH_CM = 100
MAP_HEIGHT_CM = 300
MAP_MARGIN_CM = 10
MAP_CM_PER_PIXELS = 3


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Waypoint Generator")
        self.exit = False
        self.map_x_size = self.centimeters_to_pixel(MAP_WIDTH_CM)
        self.map_y_size = self.centimeters_to_pixel(MAP_HEIGHT_CM)

        self.margin_pixels = MAP_MARGIN_CM * MAP_CM_PER_PIXELS
        width = self.map_x_size + self.margin_pixels * 2
        height = self.map_y_size + self.margin_pixels * 2
        self.screen = pygame.display.set_mode((width, height))
        self.waypoint_list = []

    def centimeters_to_pixel(self, centimeters):
        return centimeters * MAP_CM_PER_PIXELS
    
    def save_waypoint_list(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        map_path = os.path.join(current_dir, "waypoints", WAYPOINT_LIST_NAME)

        with open(map_path, "w") as f:
            for point in self.waypoint_list:
                f.write(f"{point[0]},{point[1]}\n")

    def coord_cm_to_pixel(self, point):
        x_val_pixel = (point[0] + MAP_MARGIN_CM) * MAP_CM_PER_PIXELS
        y_val_pixel = (point[1] + MAP_MARGIN_CM) * MAP_CM_PER_PIXELS
        return x_val_pixel, y_val_pixel
    
    def draw_points(self):
        for waypoint in self.waypoint_list:
                x_val_pixel, y_val_pixel = self.coord_cm_to_pixel(waypoint)
                pygame.draw.circle(self.screen, (255, 0, 255), (x_val_pixel, y_val_pixel), 3)

    def run(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        map_path = os.path.join(current_dir, "img_filtered", INPUT_MAP_NAME)
        custom_map = pygame.image.load(map_path)
        resized_custom_map = pygame.transform.scale(custom_map, (self.map_x_size, self.map_y_size))
        self.screen.blit(resized_custom_map, (self.margin_pixels, self.margin_pixels))
        pygame.display.flip()

        while not self.exit:
            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_waypoint_list()
                    self.exit = True

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    x_val_cm = (pos[0] / MAP_CM_PER_PIXELS) - MAP_MARGIN_CM
                    y_val_cm = (pos[1] / MAP_CM_PER_PIXELS) - MAP_MARGIN_CM
                    coord = (x_val_cm, y_val_cm)
                    print(f"Mouse clicked at ({pos[0]}, {pos[1]})")

                    print(f"Mouse clicked at ({coord[0]}, {coord[1]})")
                    self.waypoint_list.append(coord)
                    self.draw_points()
                    
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                    print("Backspace key pressed")
                    if (len(self.waypoint_list) > 0):
                        self.screen.fill((0, 0, 0))
                        self.screen.blit(resized_custom_map, (self.margin_pixels, self.margin_pixels))
                        self.waypoint_list.pop()
                    self.draw_points()
                    

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_DELETE:
                    print("Delete key pressed")
                    if (len(self.waypoint_list) > 0):
                        self.screen.fill((0, 0, 0))
                        self.screen.blit(resized_custom_map, (self.margin_pixels, self.margin_pixels))
                        self.waypoint_list.pop()
                    self.draw_points()                    

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    print("List saved")
                    self.save_waypoint_list()
                    

            pygame.display.flip()

            

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()