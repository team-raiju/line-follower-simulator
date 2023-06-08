from gym import Env
from gym.spaces import Box, Dict
import numpy as np
from robot import Robot
import pygame
import os
from generate_track import Map
from pygame.math import Vector2
from load_track import LoadMap


from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.vec_env import VecFrameStack
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold

HOME_DIR = os.path.dirname(__file__)

MAP_FILE_NAME = "map3.png"
MAP_WIDTH_CM = 545
MAP_HEIGHT_CM = 595
MAP_MARGIN_CM = (50/1.5)
MAP_CM_PER_PIXELS = 1.5

ROBOT_SIZE_X_CM = 12
ROBOT_SIZE_Y_CM = 6
ROBOT_INIT_POS_X_CM = 230
ROBOT_INIT_POS_Y_CM = 44
ROBOT_INIT_ANGLE = 0

WAYPOINT_LIST_NAME = "waypoints_map3.txt"

class LineFollowerEnv(Env):
    def __init__(self):

        # Env
        self.action_space = Box(low=-1, high=1, shape=(2, ), dtype=np.float32)
        self.observation_space = Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), 
                                     high=np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]), dtype=np.int32)

        pygame.init()
        pygame.display.set_caption("Line Follower")

        self.max_duration = 2000
        self.tick_rate = 60 # Hertz tick_rate = 1 / self.tick_period
        self.tick_period = 1 / self.tick_rate

        self.map_width_pixels = MAP_WIDTH_CM * MAP_CM_PER_PIXELS
        self.map_height_pixels = MAP_HEIGHT_CM * MAP_CM_PER_PIXELS

        margin_pixels = MAP_MARGIN_CM * MAP_CM_PER_PIXELS
        self.screen_width = self.map_width_pixels + (2 * margin_pixels)
        self.screen_height = self.map_height_pixels + (2 * margin_pixels)

        self.screen = pygame.display.set_mode((self.screen_width , self.screen_height))
        self.clock = pygame.time.Clock()
        self.exit = False
        self.last_error = 0

        current_dir = os.path.dirname(os.path.abspath(__file__))
        robot_image_path = os.path.join(current_dir, "media" , "raiju.png")
        robot_image = pygame.image.load(robot_image_path)

        self.robot = Robot(MAP_CM_PER_PIXELS, ROBOT_INIT_POS_X_CM, ROBOT_INIT_POS_Y_CM, ROBOT_INIT_ANGLE)
        self.resized_robot_img = pygame.transform.scale(robot_image, (self.robot.centimeters_to_pixel(ROBOT_SIZE_Y_CM), self.robot.centimeters_to_pixel(ROBOT_SIZE_X_CM)))

        self.map = LoadMap(self.screen)
        self.map.load_map_from_file(MAP_FILE_NAME, margin_pixels, self.map_width_pixels, self.map_height_pixels)

        self.load_waypoint_list()
        

    def load_waypoint_list(self):
        self.waypoint_list = []
        current_dir = os.path.dirname(os.path.abspath(__file__))
        waypoint_list_path = os.path.join(current_dir, "image_conversion", "waypoints", WAYPOINT_LIST_NAME)

        with open(waypoint_list_path, "r") as f:
            for line in f:
                x, y = line.strip().split(",")
                point = Vector2(int(x), int(y))
                self.waypoint_list.append(point)

    def draw_robot(self):
        rotated = pygame.transform.rotate(self.resized_robot_img, self.robot.angle)
        rect = rotated.get_rect()
        self.screen.blit(rotated, self.robot.position - (rect.width / 2, rect.height / 2))

    def draw_map(self):
        self.map.draw_loaded_map()
    
    def near_waypoint(self, point: Vector2, point_2: Vector2):
        distance = point.distance_to(point_2)
        max_dist_cm = 15
        if (abs(distance) < max_dist_cm * MAP_CM_PER_PIXELS):
            return True
        return False

    def step(self, action):
        
        # Action

        # last_mot_vel_l = self.robot.mot_vel_l / 100.0
        # last_mot_vel_r = self.robot.mot_vel_r / 100.0
        last_line_sensor = self.robot.get_line_sensor(self.screen, self.screen_width , self.screen_height)

        mot_left = int(action[0] * 100)
        mot_right = int(action[1] * 100)
        self.robot.motor_l.set_voltage(mot_left)
        self.robot.motor_r.set_voltage(mot_right)
        
        self.robot.update(self.tick_period)
        line_sensor = self.robot.get_line_sensor(self.screen, self.screen_width , self.screen_height)


        # Observation
        obs_np_1 = np.asarray(last_line_sensor, dtype=np.int32)
        obs_np_2 = np.asarray(line_sensor, dtype=np.int32)
        obs_np = np.append(obs_np_1, obs_np_2)

        # Reward
        reward = -0.05

        current_point = self.waypoint_list[self.waypoint_idx]
        if (self.near_waypoint(self.robot.position, current_point)):
                multiplier = self.waypoint_idx
                reward = 3000 / len(self.waypoint_list) + multiplier
                self.waypoint_idx += 1

        # Done
        done = False

        if (self.waypoint_idx >= len(self.waypoint_list)):
            reward = +1000
            done = True
        
        elif ((2000 - self.max_duration) > (1 + self.waypoint_idx) * 200):
            reward = -100
            done = True

        elif (self.robot.out_of_line(self.screen, self.screen_width , self.screen_height)):
            reward = -100
            done = True

        self.max_duration -= 1 
        if self.max_duration <= 0:
            done = True
        
        info = {}
        
        return obs_np, reward, done, info

    def render(self):
        self.screen.fill((0, 0, 0))
        self.draw_map()
        self.draw_robot()
        
        pygame.display.flip()
        self.clock.tick(self.tick_rate)
    
    def reset(self):
        self.max_duration = 2000
        self.waypoint_idx = 0
        self.robot = Robot(MAP_CM_PER_PIXELS, ROBOT_INIT_POS_X_CM, ROBOT_INIT_POS_Y_CM, ROBOT_INIT_ANGLE)
        line_sensor = self.robot.get_line_sensor(self.screen, self.screen_width, self.screen_height)
        obs_np = np.asarray(line_sensor, dtype=np.int32)
        # obs_np = np.append(obs_np, [0, 0])
        obs_np = np.append(obs_np, obs_np)


        return obs_np


#######################################################################


def train_model(iterations, name):
    PPO_Path = os.path.join(HOME_DIR, 'New_Map_Model_1', name)
    log_path = os.path.join(HOME_DIR, 'logs')

    stop_callback = StopTrainingOnRewardThreshold(reward_threshold=5850, verbose = 1)
    eval_callback = EvalCallback(env, callback_on_new_best=stop_callback, eval_freq=10000, verbose=1 , best_model_save_path=PPO_Path)

    model = PPO('MlpPolicy', env, verbose = 1, tensorboard_log=log_path)
    model.learn(total_timesteps=iterations, callback=eval_callback)



def train_existing_model(model: PPO, iterations, name):
    PPO_Path = os.path.join(HOME_DIR, 'Models_7', name)
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

    PPO_Path_Init = os.path.join(HOME_DIR, 'Models', 'Models_Best','PPO_Model_Raijin_Callback', 'best_model')
    model = PPO.load(PPO_Path_Init, env=env)

    # train_existing_model(model, 200000, 'PPO_Model_Raijin_1M200k' )
    # train_model(400000, 'PPO_Model_400k' )
    
    run_simulation(model, 4)


    