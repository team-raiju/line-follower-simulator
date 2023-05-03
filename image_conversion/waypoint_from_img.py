import os
import pygame


INPUT_MAP_NAME = "gimp-filter-rsm-2023.png"
WAYPOINT_LIST_NAME = "waypoints.txt"

MAP_X_SIZE_CM = 230
MAP_Y_SIZE_CM = 395


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Waypoint Generator")
        self.exit = False
        self.map_x_size = self.centimeters_to_pixel(MAP_X_SIZE_CM)
        self.map_y_size = self.centimeters_to_pixel(MAP_Y_SIZE_CM)

        self.margin = 100 # pixels
        width = self.map_x_size + self.margin
        height = self.map_y_size + self.margin
        self.screen = pygame.display.set_mode((width, height))
        self.waypoint_list = []

    def centimeters_to_pixel(self, centimeters):
        return centimeters * 2
    
    def save_waypoint_list(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        map_path = os.path.join(current_dir, "waypoints", WAYPOINT_LIST_NAME)

        with open(map_path, "w") as f:
            for point in self.waypoint_list:
                f.write(f"{point[0]},{point[1]}\n")


    def run(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        map_path = os.path.join(current_dir, "img_filtered", INPUT_MAP_NAME)
        custom_map = pygame.image.load(map_path)
        resized_custom_map = pygame.transform.scale(custom_map, (self.map_x_size, self.map_y_size))
        self.screen.blit(resized_custom_map, (self.margin / 2, self.margin / 2))
        pygame.display.flip()

        while not self.exit:
            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_waypoint_list()
                    self.exit = True

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    print(f"Mouse clicked at ({pos[0]}, {pos[1]})")
                    self.waypoint_list.append(pos)
                    
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                    print("Backspace key pressed")
                    if (len(self.waypoint_list) > 0):
                        self.screen.fill((0, 0, 0))
                        self.screen.blit(resized_custom_map, (self.margin / 2, self.margin / 2))
                        self.waypoint_list.pop()

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_DELETE:
                    print("Delete key pressed")
                    if (len(self.waypoint_list) > 0):
                        self.screen.fill((0, 0, 0))
                        self.screen.blit(resized_custom_map, (self.margin / 2, self.margin / 2))
                        self.waypoint_list.pop()
                
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    self.save_waypoint_list()
                    
            for waypoint in self.waypoint_list:
                pygame.draw.circle(self.screen, (255, 0, 255), (waypoint[0], waypoint[1]), 3)

            pygame.display.flip()

            

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()