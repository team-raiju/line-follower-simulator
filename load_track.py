import pygame
from pygame.math import Vector2
import os

class LoadMap:
    def __init__(self, screen):
        self.screen = screen    

    def load_map_from_file(self, file_name, margin_size, width, height):
        self.margin_size = margin_size
        current_dir = os.path.dirname(os.path.abspath(__file__))
        map_path = os.path.join(current_dir, "maps" , file_name)
        custom_map = pygame.image.load(map_path)
        self.resized_custom_map = pygame.transform.scale(custom_map, (width, height))
    
    def draw_loaded_map(self):
        self.screen.blit(self.resized_custom_map, (self.margin_size, self.margin_size))
         


def main(): 
    print("Loading track")

if __name__ == '__main__':
    main()