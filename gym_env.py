from gym import Env
from gym.spaces import Discrete, Box
import numpy as np
import random
from diff_drive import Car
import pygame
import os



class LineFollowerEnv(Env):
    def __init__(self):
        # Actions we can take, down, stay, up
        self.action_space = Discrete(3)

        # Temperature array
        self.observation_space = Box(low=np.array([0]), high=np.array([100]))

        self.car = Car(20, 10)

        # Set shower length
        self.shower_length = 60

        # Render options
        pygame.init()
        pygame.display.set_caption("Raijin")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "raiju.png")
        self.car_image = pygame.image.load(image_path)
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.tick_period_ms = 0.05 
        self.tick_rate = 1 / self.tick_period_ms
        
    def step(self, action):
        # Apply action
        # 0 -1 = -1 temperature
        # 1 -1 = 0 
        # 2 -1 = 1 temperature 

        self.car.desired_wl = 0
        self.car.desired_wr = 0
        
        if action == 0:
            self.car.desired_wl = 20
            self.car.desired_wr = 20
        elif action == 1:
            self.car.desired_wl = -20
            self.car.desired_wr = -20

        # if action == 2:
        #     self.car.desired_wl = -20
        #     self.car.desired_wr = 20

        self.car.update(self.tick_period_ms)

        # Reduce shower length by 1 second
        self.shower_length -= 1 
        
        # Calculate reward
        if self.car.desired_wl >=17 and self.car.desired_wl <=23: 
            reward = 1 
        else: 
            reward = -1 
        
        # Check if shower is done
        if self.shower_length <= 0: 
            done = True
        else:
            done = False
        
        info = {}
        
        # Return step information
        return self.car.desired_wl, reward, done, info

    def render(self):
        # Implement viz
        self.screen.fill((0, 0, 0))
        rotated = pygame.transform.rotate(self.car_image, self.car.angle)
        rect = rotated.get_rect()
        ppu = 32
        self.screen.blit(rotated, self.car.position * ppu - (rect.width / 2, rect.height / 2))
        pygame.display.flip()
        self.clock.tick(self.tick_rate)
    
    def reset(self):
        # Reset shower time
        self.shower_length = 60 
        self.car.desired_wl = 0
        self.car.desired_wr = 0
        return self.car.desired_wl

env = LineFollowerEnv()
# print(env.observation_space.sample())

episodes = 2
for episode in range(1, episodes+1):
    state = env.reset()
    done = False
    score = 0 
    
    while not done:
        env.render()
        print(env.car.desired_wl)
        action = env.action_space.sample()
        n_state, reward, done, info = env.step(action)
        score+=reward
    print('Episode:{} Score:{}'.format(episode, score))