#!/usr/bin/env python3
# -*- coding: utf-8 -*-q

#color code(R=赤, B=青, G=緑)を受け取りそのhsvそれぞれのminとmaxを返す
def hsv_color(c_code):

    if c_code == 'R':
        hsv_min = (0, 200, 77)
        hsv_max = (15, 255, 255)
    # elif c_code == 'B':
    #     hsv_min = (83, 0, 30)
    #     hsv_max = (140, 255, 255)
    # elif c_code == 'G':
    #     hsv_min = (50, 100, 70)
    #     hsv_max = (77, 255, 115)

    # if c_code == 'DR':            #Dark Red
    #     hsv_min = (0, 170, 20)
    #     hsv_max = (15, 255, 255)
    elif c_code == 'G':            #Dark Green
        hsv_min = (40, 50, 20)
        hsv_max = (80, 255, 255)
    elif c_code == 'B':             #Dark Blue
        hsv_min = (85, 50, 50)
        hsv_max = (100, 255, 255)

    return hsv_min, hsv_max
