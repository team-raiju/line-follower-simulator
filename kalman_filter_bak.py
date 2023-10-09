import numpy as np
import matplotlib.pyplot as plt

PI = 3.14159265358979323846


A_k_minus_1 = np.array([[1.0,  0,   0],
                        [  0,1.0,   0],
                        [  0,  0, 1.0]])

     
                 
H_k = np.array([0,  0, 1])

# Observation covariance in yaw                    
R_k = (0.001 ** 2)

# Last Z obs         
PreZt = 0

# sensor_noise_w_k = np.array([0, 0, 0.001])
sensor_noise_w_k = 0.001
 


# Predicted covariance of the state equation
def getQk(yaw, delta_s, delta_yaw):
    alpha = 0.1
    W_k = np.array([[np.cos(yaw + delta_yaw / 2), (-delta_s / 2) * np.sin(yaw + delta_yaw / 2)],
                     [np.sin(yaw + delta_yaw / 2), (delta_s / 2) * np.cos(yaw + delta_yaw / 2)],
                     [0, 1]])

    Error_params = np.array([[alpha * delta_s ** 2 + alpha * delta_yaw ** 2, 0],
                            [0, alpha * delta_s ** 2 + alpha * delta_yaw ** 2]])
    

    return W_k @ Error_params @ W_k.T

    # return np.array([[1.0,   0,   0],
    #             [  0, 1.0,   0],
    #             [  0,   0, 1.0]])
                    

def getB(yaw, delta_s, delta_yaw):
    B = np.array([np.cos(yaw + delta_yaw / 2) * delta_s, np.sin(yaw + delta_yaw / 2) * delta_s, delta_yaw])
    return B
 
def ekf(z_k_observation_vector, state_estimate_k_minus_1, 
        control_vector_k_minus_1, P_k_minus_1, dk):

    process_noise_v_k_minus_1 = np.array([0.01 * np.random.randn(), 0.01 * np.random.randn() , 0.01 * np.random.randn() ])

    state_estimate_k = A_k_minus_1 @ (state_estimate_k_minus_1) + (
        getB(state_estimate_k_minus_1[2], control_vector_k_minus_1[0], control_vector_k_minus_1[1])) + (process_noise_v_k_minus_1)
             
    # print(f'State Estimate Before EKF={state_estimate_k}')
             
    Fk_minus_1 = CalcFk(state_estimate_k_minus_1, control_vector_k_minus_1)

    P_k = Fk_minus_1 @ P_k_minus_1 @ Fk_minus_1.T + getQk(state_estimate_k_minus_1[2], control_vector_k_minus_1[0], control_vector_k_minus_1[1])
         
    measurement_residual_y_k = z_k_observation_vector - ( state_estimate_k[2] + (sensor_noise_w_k))
             
    S_k = P_k[2][2] + R_k
         
    K_k = (P_k @ H_k.T) * (1 / S_k)
         
    # Calculate an updated state estimate for time k
    state_estimate_k[2] = state_estimate_k[2] + (K_k[2] * measurement_residual_y_k)
     
    # Update the state covariance estimate for time k
    P_k = (1 - K_k[2]) * P_k
    # print(P_k)
    # print(f'State Estimate After EKF={state_estimate_k}')

    return state_estimate_k, P_k

def CalcTruePosition(position, robot_input):
    dS, dTh = robot_input
    position[0] += dS * np.cos(position[2] + dTh / 2)
    position[1] += dS * np.sin(position[2] + dTh / 2)
    position[2] += dTh

def CalcPositionWithError(position, robot_input):
    dS, dTh = robot_input
    sigma = np.array([0.0, 0.0])

    calc_qk = getQk(position[2], robot_input[0], robot_input[1])
    sigma[0] = calc_qk[0,0]
    sigma[1] = calc_qk[0,0]
    dS += np.random.randn() * np.sqrt(sigma[0])
    dTh += np.random.randn() * np.sqrt(sigma[1])

    # dS += np.random.randn() * 0.01
    # dTh += np.random.randn() * 0.01
    
    CalcPosition(position, [dS, dTh])

def CalcPosition(position, robot_input):
    pre_x, pre_y, pre_th = position
    dS, dTh = robot_input
    position[0] = pre_x + dS * np.cos(pre_th + dTh / 2)
    position[1] = pre_y + dS * np.sin(pre_th + dTh / 2)
    position[2] = pre_th + dTh


def CalcFk(pre, robot_input):
    dS, dTh = robot_input
    pre_x, pre_y, pre_th = pre
    return np.array([[1, 0, -dS * np.sin(pre_th + dTh / 2)],
                     [0, 1, dS * np.cos(pre_th + dTh / 2)],
                     [0, 0, 1]])
    # return np.array([[1, 0, 0],
    #                  [0, 1, 0],
    #                  [0, 0, 1]])


def CalcU(robot_input, dt):
    Tred = 0.1

    velo_tra, velo_rot = robot_input
    Vr = (velo_rot * Tred + 2 * velo_tra) / 2
    Vl = (-velo_rot * Tred + 2 * velo_tra) / 2
    dSr = Vr * dt
    dSl = Vl * dt
    dS = (dSr + dSl) / 2
    dTh = (dSr - dSl) / Tred
    return [dS, dTh]

def GetIMU(pre, u, dt):
    noise_imu = (0.001 ** 2)

    new_z = pre + u * dt + np.random.normal(0, np.sqrt(noise_imu))
    return new_z

def main():

    true_position_history = []
    odo_position_history = []
    ekf_position_history = []

 
    # We start at time k=1
    k = 1
     
    # Time interval in seconds
    dk = 0.1
 
    state_estimate_k_minus_1 = np.array([0.0,0.0,0.0])
     
    control_vector_velocity = np.array([1.0, 0.1])
     
    P_k_minus_1 = np.array([[0,  0,   0],
                            [  0, 0.,   0],
                            [  0,  0, 0]])

    time = 0.0
    ContinueTime = 60.0  # [s]
    Step = int((ContinueTime - time) / dk) + 1

    TruePosition = np.array([0.0, 0.0, 0.0])
    OdoPosition = np.array([0.0, 0.0, 0.0])  # [x, y, th]


    for k in range(Step):

        global PreZt

        control_vector_k_minus_1 = CalcU(control_vector_velocity, dk)

        CalcTruePosition(TruePosition, control_vector_k_minus_1)

        # Update odometry position with noise
        CalcPositionWithError(OdoPosition, control_vector_k_minus_1)

        z_k_observation_vector = GetIMU(PreZt, control_vector_velocity[1], dk)

     
        # Print the current timestep
        # print(f'Timestep k={k}')  
         
        # Run the Extended Kalman Filter and store the 
        # near-optimal state and covariance estimates
        optimal_state_estimate_k, covariance_estimate_k = ekf(
            z_k_observation_vector, # Most recent sensor measurement
            state_estimate_k_minus_1, # Our most recent estimate of the state
            control_vector_k_minus_1, # Our most recent control input
            P_k_minus_1, # Our most recent state covariance matrix
            dk) # Time interval
         
        # Get ready for the next timestep by updating the variable values
        state_estimate_k_minus_1 = optimal_state_estimate_k
        P_k_minus_1 = covariance_estimate_k
        PreZt = z_k_observation_vector
         

        if k % 10 == 0:
            true_position_history.append(TruePosition.copy())
            odo_position_history.append(OdoPosition.copy())
            ekf_position_history.append(optimal_state_estimate_k.copy())
        
        
        
        # Print a blank line
        # print()

    true_position_history = np.array(true_position_history)
    odo_position_history = np.array(odo_position_history)
    ekf_position_history = np.array(ekf_position_history)

    # Plot the results
    plt.figure(figsize=(10, 6))
    plt.plot(true_position_history[:, 0], true_position_history[:, 1], '.b', label='True')
    plt.plot(odo_position_history[:, 0], odo_position_history[:, 1], '.k', label='Odometry')
    plt.plot(ekf_position_history[:, 0], ekf_position_history[:, 1], '.r', label='EKF')
    plt.axis('equal')
    plt.legend()
    plt.title('Robot Position Estimation')
    plt.xlabel('X (m)')
    plt.ylabel('Y (m)')
    plt.grid(True)
    plt.show()



 
# Program starts running here with the main method  
main()