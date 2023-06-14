#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @brief 最小二乗法による円フィッティングモジュール
# @author: Atsushi Sakai

import numpy as np
import math
import os

def CircleFitting(x, y):
    sumx = sum(x)
    sumy = sum(y)
    sumx2 = sum([ix**2 for ix in x])
    sumy2 = sum([iy**2 for iy in y])
    sumxy = sum([ix * iy for (ix, iy) in zip(x, y)])

    F = np.array([[sumx2, sumxy, sumx], [sumxy, sumy2, sumy], [sumx, sumy, len(x)]])

    G = np.array(
        [
            [-sum([ix**3 + ix * iy**2 for (ix, iy) in zip(x, y)])],
            [-sum([ix**2 * iy + iy**3 for (ix, iy) in zip(x, y)])],
            [-sum([ix**2 + iy**2 for (ix, iy) in zip(x, y)])],
        ]
    )

    T = np.linalg.inv(F).dot(G)

    cxe = float(T[0] / -2)
    cye = float(T[1] / -2)
    re = math.sqrt(cxe**2 + cye**2 - T[2])

    # print (cxe)
    # print (cye)
    print ("re: " + str(re))
    return (cxe, cye, re)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "map5_track.txt")
    file_path_2 = os.path.join(current_dir, "samples.txt")

    x = []
    y = []
    circle_count = []
    with open(file_path, "r") as file:
        for line in file:
            my_x, my_y = line.strip().split(",")
            x.append(float(my_x))
            y.append(float(my_y))

    with open(file_path_2, "r") as file:
        for line in file:
            count = line.strip()
            circle_count.append(int(count))

    # 円フィッティング
    index = 0
    for i in range(len(circle_count)):
        if (circle_count[i] - index) < 3:
            index = circle_count[i]
            print("invalid")
        else:
            (cxe, cye, re) = CircleFitting(x[index : circle_count[i]], y[index : circle_count[i]])

            # 円描画
            theta = np.arange(0, 2 * math.pi, 0.1)
            xe = []
            ye = []
            errors = []
            for itheta in theta:
                xe.append(re * math.cos(itheta) + cxe)
                ye.append(re * math.sin(itheta) + cye)

            xe.append(xe[0])
            ye.append(ye[0])

            size = circle_count[i] - index

            errors = []
            for j in range(size):
                real_r_squared = (x[index + j] - cxe) ** 2 + (y[index + j] - cye) ** 2
                error = real_r_squared - re**2
                errors.append(error)
                
            
            rmse = math.sqrt(sum([error**2 for error in errors]) / len(errors))
            print("error: " + str(rmse))


            plt.gca().invert_yaxis()
            plt.plot(x[index : circle_count[i]], y[index : circle_count[i]], "ob", label="raw data")
            plt.plot(xe, ye, "-r", label="estimated")
            plt.plot(cxe, cye, "xb", label="center")
            plt.axis("equal")
            plt.grid(True)
            plt.legend()
            plt.show()

            index = circle_count[i]
