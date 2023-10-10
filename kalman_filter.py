import numpy as np
import matplotlib.pyplot as plt
import math


class KalmanFilter:

    def __init__(self, alpha_param, rk_param, inital_xt):

        # Robot parameter for estimating erros
        self.alpha = np.array([alpha_param, alpha_param, alpha_param, alpha_param])  # [a1, a2, a3, a4]

        # Position initialization
        self.state_estimate_k_minus_1 = np.array(inital_xt)

        # Dispersion initialization
        self.P_k_minus_1 = np.zeros((3, 3))

        # IMU noise
        self.sensor_noise_w_k = 0.001

        # Observation covariance in yaw                    
        self.R_k = rk_param

                
    def getB(self, yaw_minus_1, delta_s, delta_yaw):
        B = np.array([np.cos(-(yaw_minus_1 + delta_yaw / 2)) * delta_s, np.sin(-(yaw_minus_1 + delta_yaw / 2)) * delta_s, delta_yaw])
        return B
    
    def getA(self):
        return np.array([[1.0,  0,   0],
                        [  0,1.0,   0],
                        [  0,  0, 1.0]])


    def CalcRt(self, param, robot_input):
        return np.array([[param[0] * robot_input[0]**2 + param[1] * robot_input[1]**2, 0],
                        [0, param[2] * robot_input[0]**2 + param[3] * robot_input[1]**2]])

    def CalcFk(self, yaw_minus_1, robot_input):
        dS, dTh = robot_input
        return np.array([[1, 0, -dS * np.sin(-(yaw_minus_1 + dTh / 2))],
                        [0, 1, dS * np.cos(-(yaw_minus_1 + dTh / 2))],
                        [0, 0, 1]])
    
    # Predicted covariance of the state equation
    def getQk(self, yaw_minus_1, delta_s, delta_yaw):
        W_k = np.array([[np.cos(-(yaw_minus_1 + delta_yaw / 2)), (-delta_s / 2) * np.sin(-(yaw_minus_1 + delta_yaw / 2))],
                        [np.sin(-(yaw_minus_1 + delta_yaw / 2)), (delta_s / 2) * np.cos(-(yaw_minus_1 + delta_yaw / 2))],
                        [0, 1]])

        Error_params = np.array([[self.alpha[0] * delta_s ** 2 + self.alpha[1] * delta_yaw ** 2, 0],
                                [0, self.alpha[2] * delta_s ** 2 + self.alpha[3] * delta_yaw ** 2]])

        # return np.array([[1.0,   0,   0],
        #             [  0, 1.0,   0],
        #             [  0,   0, 1.0]])

        return W_k @ Error_params @ W_k.T


    def KalmanFilterRunStep(self, delta_s, delta_theta, angle_imu):

        delta_theta_rad = math.radians(delta_theta)
        angle_imu_rad = math.radians(angle_imu)

        control_vector_k_minus_1 = [delta_s, delta_theta_rad]

        # Calculate process noise. (Encoder noise)
        process_noise_v_k_minus_1 = np.array([0.01 * np.random.randn(), 0.01 * np.random.randn() , 0.01 * np.random.randn() ])

        state_estimate_k = self.getA() @ (self.state_estimate_k_minus_1) + (
            self.getB(self.state_estimate_k_minus_1[2], control_vector_k_minus_1[0], control_vector_k_minus_1[1])) + (process_noise_v_k_minus_1)


        Fk_minus_1 = self.CalcFk(self.state_estimate_k_minus_1[2], control_vector_k_minus_1)

        P_k = Fk_minus_1 @ self.P_k_minus_1 @ Fk_minus_1.T + self.getQk(self.state_estimate_k_minus_1[2], control_vector_k_minus_1[0], control_vector_k_minus_1[1])

        measurement_residual_y_k = angle_imu_rad - ( state_estimate_k[2] + (self.sensor_noise_w_k))

        S_k = P_k[2][2] + self.R_k
        H_k = np.array([0, 0, 1])
        K_k = (P_k @ H_k.T) * (1 / S_k)

        # Calculate an updated state estimate for time k
        state_estimate_k[2] = state_estimate_k[2] + (K_k[2] * measurement_residual_y_k)

        P_k = (1 - K_k[2]) * P_k

        # Update variables for next iteration
        self.state_estimate_k_minus_1 = state_estimate_k
        self.P_k_minus_1 = P_k

        return [state_estimate_k[0], state_estimate_k[1], math.degrees(state_estimate_k[2])] # [x, y, theta]