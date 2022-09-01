#!/usr/bin/env python3
# -*- coding: utf-8 -*-q

#color code(R=赤, B=青, G=緑)を受け取りそのhsvそれぞれのminとmaxを返す
def hsv_color(c_code):

    if c_code == 'R':
        hsv_min = (0, 200, 77)
        hsv_max = (15, 255, 255)
    elif c_code == 'B':
        hsv_min = (83, 0, 30)
        hsv_max = (140, 255, 255)
    elif c_code == 'G':
        hsv_min = (50, 100, 70)
        hsv_max = (77, 255, 115)

    return hsv_min, hsv_max
