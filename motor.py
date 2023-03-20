import numpy as np
import matplotlib.pyplot as plt
import math

class Motor:
    def __init__(self, wheel_radius_cm):
        self.max_voltage = 12.6 # Volts
        self.voltage = self.max_voltage

        self.positive_voltage = True

        self.battery_resistance = 0.03 # Ohms

        self.kv = 2710 # RPM/V
        self.kv_rad = (1/self.kv) / 0.10472 # V/(rad/s)
        self.kt = 0.00352 #Nm/A
        self.total_motor_r = 1.45 # Omhs (motor_resistance/2 as we have 2 motors)
        self.inercial_momentum = 1.51 * pow(10, -8) # kg.m²

        self.gear_ratio = 1 / 6
        self.wheel_radius_m = wheel_radius_cm * 0.01 # Meters
        self.efficency = 0.95
        self.mass = 0.12 # Kg
        self.atrict_coef = 1
        self.normal_brushless = 3 # Newton
        self.Ir = 2 * self.inercial_momentum * 1.1 # Total inercial moment (1.1 is estimation)
        self.move_resistance = self.normal_brushless + self.mass * 9.8 # Newton

        # Calculations
        self.aux = (self.battery_resistance + self.total_motor_r) / (self.kv_rad * self.kt)
        self.aux_2 = pow((self.gear_ratio * self.wheel_radius_m), 2) / self.efficency 

        self.time_constant = self.aux * (self.Ir + self.aux_2 * self.mass ) # seconds

        self.v_inf = ((self.gear_ratio * self.wheel_radius_m) * self.voltage / self.kv_rad) - (self.aux * self.aux_2 * self.move_resistance) # Equilibrium velocity (m/s)


    def set_voltage(self, percentage):
        if percentage < -100:
            percentage = -100
        elif percentage > 100:
            percentage = 100
        
        if percentage < 0:
            self.positive_voltage = False
            self.voltage = self.max_voltage * -percentage / 100
        else:
            self.positive_voltage = True
            self.voltage = self.max_voltage * percentage / 100
            


    def velocity_time_t(self, t):
        self.v_inf = ((self.gear_ratio * self.wheel_radius_m) * self.voltage / self.kv_rad) - (self.aux * self.aux_2 * self.move_resistance)
        if self.v_inf < 0:
            self.v_inf = 0

        if (self.positive_voltage):
            return self.v_inf * (1 - math.exp(-(t)/self.time_constant))
        return  -self.v_inf * (1 - math.exp(-(t)/self.time_constant))

    
    def time_of_velocity(self, v_t):
        self.v_inf = ((self.gear_ratio * self.wheel_radius_m) * self.voltage / self.kv_rad) - (self.aux * self.aux_2 * self.move_resistance)
        if self.v_inf < 0:
            self.v_inf = 0
        
        if (self.positive_voltage):
            return -self.time_constant * math.log(1 - (v_t / self.v_inf))
        
        return -self.time_constant * math.log(1 - (v_t / -self.v_inf))
    
    def velocity_after_interval(self, v_0, delta_t):
        self.v_inf = ((self.gear_ratio * self.wheel_radius_m) * self.voltage / self.kv_rad) - (self.aux * self.aux_2 * self.move_resistance)
        if self.v_inf < 0:
            self.v_inf = 0
        
        if (self.positive_voltage):
            vel = (self.v_inf - v_0) * (1 - math.exp(-(delta_t)/self.time_constant)) + v_0
        else:
            vel = (-self.v_inf - v_0) * (1 - math.exp(-(delta_t)/self.time_constant)) + v_0

        if abs(vel) < 0.00001:
            return 0
    
        return vel
    
    def plot_velocity_time(self):
        t = np.linspace(0,2,200)
        y = np.vectorize(self.velocity_time_t)(t)

        fig = plt.figure()
        ax = fig.add_subplot()
        ax.plot(t, y)
        ax.set_title('Motor velocity')
        ax.set_xlabel('t(s)')
        ax.set_ylabel('Y(m/s)')
        plt.show()


    def plot_distance_time(self):
        t = np.linspace(0, 2, 200)
        y =  np.array([])
        dist = 0

        for i in range(200):
            dist += (self.velocity_time_t(t[i])) * 0.01
            y = np.append(y, dist)
        
        fig = plt.figure()
        ax = fig.add_subplot()
        ax.plot(t, y)
        ax.set_title('Motor velocity')
        ax.set_xlabel('t(s)')
        ax.set_ylabel('Y(m)')
        plt.show()

    def plot_break_time(self):
        t = np.linspace(0, 2, 200)
        y =  np.array([])
        vel = 5.6
        self.v_inf = -5.6

        for i in range(200):
            vel = self.velocity_after_interval_2(vel, 0.01)
            y = np.append(y, vel)
        
        fig = plt.figure()
        ax = fig.add_subplot()
        ax.plot(t, y)
        ax.set_title('Motor velocity')
        ax.set_xlabel('t(s)')
        ax.set_ylabel('Y(m)')
        plt.show()


# mot = Motor(1.5)
# print(mot.time_constant)
# print(mot.v_inf)
# mot.set_voltage(0)
# print(mot.velocity_after_interval(5, 10))