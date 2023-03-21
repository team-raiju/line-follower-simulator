from gym import Env
from gym.spaces import Discrete, Box
import numpy as np
import random
from robot import Robot
import pygame
import os
from generate_track import Map
from pygame.math import Vector2


class LineFollowerEnv(Env):
    def __init__(self):

        # Env
        self.action_space = Box(low=-100, high=100, shape=(2, ), dtype=np.int16)
        self.observation_space = Box(0, 1, shape=(6,), dtype=int)

        self.max_duration = 1000

        self.robot = Robot(20, 245, 90)

        # Render options
        pygame.init()
        pygame.display.set_caption("Raijin")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "raiju.png")
        self.car_image = pygame.image.load(image_path)
        self.resized_image = pygame.transform.scale(self.car_image, (36, 36))
        self.screen = pygame.display.set_mode((1280, 810))
        self.clock = pygame.time.Clock()
        self.tick_rate = 60 # Hertz tick_rate = 1 / self.tick_period
        self.tick_period = 1 / self.tick_rate

        self.map = Map(20, 245, 270, self.screen)
        self.map.gen_default_track()

        self.waypoint_idx = 0
        
    def step(self, action):
        
        # Action
        mot_left, mot_right = action
        self.robot.motor_l.set_voltage(mot_left)
        self.robot.motor_r.set_voltage(mot_right)
        self.robot.update(self.tick_period)

        # Observation
        line_sensor = self.robot.get_line_sensor(self.screen, 1280, 810)

        # Reward
        reward = -0.1

        if (self.map.near_waypoint(self.robot.position, self.waypoint_idx)):
                self.waypoint_idx += 1
                reward = 1000 / 62 # 1000 / len(waypoints)

        # Done
        done = False

        if (self.robot.out_of_line(self.screen, 1280, 810)):
            reward = -100
            done = True

        self.max_duration -= 1 
        if self.max_duration <= 0: 
            done = True
        
        
        info = {}
        
        return line_sensor, reward, done, info

    def render(self):
        self.screen.fill((0, 0, 0))
        map = Map(20, 245, 270, self.screen)
        map.gen_default_track()

        rotated = pygame.transform.rotate(self.resized_image, self.robot.angle)
        rect = rotated.get_rect()
        self.screen.blit(rotated, self.robot.position - (rect.width / 2, rect.height / 2))
        pygame.display.flip()
        self.clock.tick(self.tick_rate)
    
    def reset(self):
        self.max_duration = 1000
        self.waypoint_idx = 0
        motor = [0, 0]
        self.robot = Robot(20, 245, 90)
        return motor




if __name__ == '__main__':
    env = LineFollowerEnv()

    episodes = 6
    for episode in range(1, episodes+1):
        state = env.reset()
        done = False
        score = 0 
        
        while not done:
            env.render()
            action = env.action_space.sample()
            n_state, reward, done, info = env.step(action)
            score+=reward
        print('Episode:{} Score:{}'.format(episode, score))