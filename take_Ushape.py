#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from djitellopy import Tello    # DJITelloPyのTelloクラスをインポート
import time                     # time.sleepを使いたいので
import cv2                      # OpenCVを使うため
import math



imgnum = 0
save_path = '/Users/ryokokubun/Desktop/drone/'

#右に移動しながら、撮影する関数
def take_rightliner(tello,dist=240,interval=20):
    # tello : tello
    # dest : 移動するトータルの距離
    # interval : 撮影する間隔

    #必要な値の宣言
    frame_read = tello.get_frame_read()
    n_dist = 0

    #１回目の撮影
    image = frame_read.frame
    cv2.imwrite(save_path+'tello'+str(imgnum)+".jpg", image)
    imgnum+=1

    #移動しながら撮影
    while n_dist < dist:
        # 移動
        tello.move_right(interval)
        # 撮影
        image = frame_read.frame
        cv2.imwrite(save_path+'tello'+str(imgnum)+".jpg", image)
        imgnum+=1

        n_dist += interval

#反時計まわりで旋回しながら撮影する関数
def take_rotate_counter(tello,radius=115,angle_t=180,angle_e=10):
    #tello : tello
    #radius : 回転する半径(指定した数字に自信持てない)
    #angle_t : 何度旋回するか（度数法）
    #angle_e : 何度間隔で撮影するか（度数法）

    #必要な値の宣言
    frame_read = tello.get_frame_read()
    angle_n = 0
    #余弦定理を用いて、横移動距離を求める
    dist_move = int(math.sqrt(2*radius*(1-math.cos(math.radians(angle_e)))))

    #１回目の撮影
    image = frame_read.frame
    cv2.imwrite(save_path+'tello'+str(imgnum)+".jpg", image)
    imgnum+=1

    #移動しながら撮影
    while angle_n < angle_t :
        # 移動
        tello.rotate_counter_clockwise(angle_e)
        tello.move_right(dist_move)
        # 撮影
        image = frame_read.frame
        cv2.imwrite(save_path+'tello'+str(imgnum)+".jpg", image)
        imgnum+=1

def take_Ushape(tello):
    take_rightliner(tello,240,20)
    take_rotate_counter(tello,115,180,10)
    take_rightliner(tello,240,20)
