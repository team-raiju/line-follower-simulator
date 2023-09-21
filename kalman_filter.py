import numpy as np
import matplotlib.pyplot as plt
import math


class KalmanFilter:

    def __init__(self):

        # Error parameters
        self.sigma = np.array([0.0, 0.0])
        self.Rt = np.array([[0.0, 0.0], [0.0, 0.0]])
        # a = np.array([0.1, 0.1, 0.1, 0.1])  # [a1, a2, a3, a4]
        self.Qt = (0.03 ** 2)

        # Position initialization
        self.PreXt = np.array([0.0, 0.0, 0.0])

        # Dispersion initialization
        self.PrePt = np.zeros((3, 3))

                
    def CalcPositionWithErrorAndReturn(self, position, robot_input):
        dS, dTh = robot_input
        pre_x, pre_y, pre_th = position

        dS += np.random.randn() * np.sqrt(self.sigma[0])
        dTh += np.random.randn() * np.sqrt(self.sigma[1])
        x = pre_x + dS * np.cos(pre_th + dTh / 2)
        y = pre_y + dS * np.sin(pre_th + dTh / 2)
        th = pre_th + dTh

        ret_array = np.array([x, y, th])
        return ret_array



    def CalcRt(self, param, robot_input):
        return np.array([[param[0] * robot_input[0]**2 + param[1] * robot_input[1]**2, 0],
                        [0, param[2] * robot_input[0]**2 + param[3] * robot_input[1]**2]])

    def CalcAt(self, pre, robot_input):
        dS, dTh = robot_input
        pre_x, pre_y, pre_th = pre
        return np.array([[1, 0, -dS * np.sin(pre_th + dTh / 2)],
                        [0, 1, dS * np.cos(pre_th + dTh / 2)],
                        [0, 0, 1]])

    def CalcWt(self, pre, robot_input):
        dS, dTh = robot_input
        pre_x, pre_y, pre_th = pre
        return np.array([[np.cos(pre_th + dTh / 2), (-dS / 2) * np.sin(pre_th + dTh / 2)],
                        [np.sin(pre_th + dTh / 2), (dS / 2) * np.cos(pre_th + dTh / 2)],
                        [0, 1]])



    def KalmanFilterRunStep(self, delta_s, delta_theta, angle_imu):
        # Calculate control robot_input

        delta_theta_rad = math.radians(delta_theta)
        angle_imu_rad = math.radians(angle_imu)

        robot_input = [delta_s, delta_theta_rad]

        # Calculate process noise
        # Rt = CalcRt(a, robot_input)
        # self.sigma[0] = Rt[0, 0]
        # self.sigma[1] = Rt[1, 1]

        self.sigma[0] = 0.05 ** 2
        self.sigma[1] = 0.05 ** 2

        # Forecast step
        EstXt = self.CalcPositionWithErrorAndReturn(self.PreXt, robot_input)
        At = self.CalcAt(self.PreXt, robot_input)
        Wt = self.CalcWt(self.PreXt, robot_input)

        self.EstPt = np.dot(np.dot(At, self.PrePt), np.transpose(At)) + np.dot(np.dot(Wt, self.Rt), np.transpose(Wt))

        # Update IMU step
        ObsZt = angle_imu_rad
        Ht = np.array([0, 0, 1])  

        
        St = np.array([np.dot(np.dot(Ht, self.EstPt), np.transpose(Ht)) + self.Qt])

        # Kt = np.linalg.solve(St * np.eye(3), np.dot(EstPt, np.transpose(Ht)))
        Kt = np.dot(np.dot(self.EstPt, np.transpose(Ht)), np.linalg.inv(St * np.eye(3)))

        EstXt = EstXt + np.dot(Kt, (ObsZt - np.dot(Ht, EstXt)))
        ExtPt = np.dot((np.identity(3) - np.dot(Kt, Ht)), self.EstPt)

        # Update variables for the next iteration
        self.PreXt = EstXt.copy()
        self.PrePt = ExtPt.copy()

        return [EstXt[0], EstXt[1], math.degrees(EstXt[2])] # [x, y, theta]