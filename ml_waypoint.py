from gym import Env
from gym.spaces import Box, Dict
import numpy as np
from robot import Robot
import pygame
import os
from generate_track import Map
from pygame.math import Vector2

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.vec_env import VecFrameStack
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.env_checker import check_env
import math


HOME_DIR = os.path.dirname(__file__)

class LineFollowerEnv(Env):
    def __init__(self):

        # Env
        self.action_space = Box(low=-1, high=1, shape=(2, ), dtype=np.float32)
        self.observation_space = Box(low=np.array([0, -180, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), 
                                     high=np.array([700, 180, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]), dtype=np.int32)

        self.max_duration = 2000

        self.robot = Robot(20, 245, 90)

        # Render options
        self.screen_width = 1280
        self.screen_height = 810

        pygame.init()
        pygame.display.set_caption("Raijin")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "media, "raiju.png")
        self.car_image = pygame.image.load(image_path)
        self.resized_image = pygame.transform.scale(self.car_image, (12, 24))
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.tick_rate = 60 # Hertz tick_rate = 1 / self.tick_period
        self.tick_period = 1 / self.tick_rate

        self.map = Map(20, 245, 270, self.screen)
        self.map.gen_default_track()

        self.waypoint_idx = 0
    
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
        
    def step(self, action):
        

        last_line_sensor = self.robot.get_line_sensor(self.screen, self.screen_width , self.screen_height)


        # Action
        mot_left = int(action[0] * 100)
        mot_right = int(action[1] * 100)
        self.robot.motor_l.set_voltage(mot_left)
        self.robot.motor_r.set_voltage(mot_right)
        self.robot.update(self.tick_period)

        # Observation
        line_sensor = self.robot.get_line_sensor(self.screen, self.screen_width , self.screen_height)
        (dist, angleDiff) = self.trackGoal(self.robot.position, self.map.waypoint[self.waypoint_idx], self.robot.angle)

        if dist > 700:
            dist = 700
        
        if (angleDiff > 180):
            angleDiff = 180
        elif angleDiff < -180:
            angleDiff = -180


        obs_np_1 = np.array([int(dist), int(angleDiff)], dtype=np.int32)
        obs_np_2 = np.asarray(last_line_sensor, dtype=np.int32)
        obs_np_3 = np.asarray(line_sensor, dtype=np.int32)
        obs_np = np.append(obs_np_1, obs_np_2)
        obs_np = np.append(obs_np, obs_np_3)


        

        # Reward
        reward = 0

        if (self.map.near_waypoint(self.robot.position, self.waypoint_idx)):
                multiplier = self.waypoint_idx
                reward = 3000 / len(self.map.waypoint) + multiplier
                self.waypoint_idx += 1


        # Done
        done = False
        # if (self.waypoint_idx >= 2):
        #     for i in range(self.waypoint_idx - 2):
        #         if (self.map.near_waypoint(self.robot.position, i)):
        #             done = True
        #             reward = -150

        if (self.waypoint_idx >= len(self.map.waypoint)):
            reward = +300
            done = True
        
        elif ((2000 - self.max_duration) > (1 + self.waypoint_idx) * 200):
            reward = -100
            done = True

        elif (self.robot.out_of_line(self.screen, self.screen_width , self.screen_height)):
            reward = -100
            done = True

        self.max_duration -= 1 
        if self.max_duration <= 0:
            reward = -100 
            done = True
        
        info = {}
        
        return obs_np, reward, done, info

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
        self.max_duration = 2000
        self.waypoint_idx = 0
        self.robot = Robot(20, 245, 90)

        line_sensor = self.robot.get_line_sensor(self.screen, self.screen_width, self.screen_height)
        obs_np_1 = np.array([0, 0], dtype=np.int32)
        obs_np_2 = np.asarray(line_sensor, dtype=np.int32)
        obs_np = np.append(obs_np_1, obs_np_2)
        obs_np = np.append(obs_np, obs_np_2)

        return obs_np





def train_model(iterations, name):
    PPO_Path = os.path.join(HOME_DIR, 'Models_8', name)
    log_path = os.path.join(HOME_DIR, 'logs')
    model = PPO('MlpPolicy', env, verbose = 1, tensorboard_log=log_path)
    model.learn(total_timesteps=iterations)
    model.save(PPO_Path)

def train_existing_model(model: PPO, iterations, name):
    PPO_Path = os.path.join(HOME_DIR, 'Models_8', name)
    model.learn(total_timesteps=iterations)
    model.save(PPO_Path)

def run_simulation(model : PPO, episodes):
    for episode in range(1, episodes+1):
        observation = env.reset()
        done = False
        score = 0 
        
        while not done:
            env.render()
            action, _ = model.predict(observation)
            observation, reward, done, info = env.step(action)
            score+=reward
        print('Episode:{} Score:{}'.format(episode, score))

if __name__ == '__main__':
    env = LineFollowerEnv()

    # PPO_Path_Init = os.path.join(HOME_DIR, 'Models_8', 'PPO_Model_Raijin_1M300k')
    # model = PPO.load(PPO_Path_Init, env=env)
    
    # train_existing_model(model, 400000, 'PPO_Model_Raijin_1M300k' )
    train_model(820000, 'PPO_Model_Raijin_820k' )
    
    # run_simulation(model, 4)


    