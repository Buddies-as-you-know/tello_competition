#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time  # time.sleepを使いたいので

import cv2  # OpenCVを使うため
import numpy as np
from djitellopy import Tello  # DJITelloPyのTelloクラスをインポート
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image


def detect_red_color(img):
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
 
    # 赤色のHSVの値域1
    hsv_min = np.array([0, 200, 77])
    hsv_max = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, hsv_min, hsv_max)
 
    # 赤色のHSVの値域2
    hsv_min = np.array([230, 200, 77])
    hsv_max = np.array([255, 255, 255])
    mask2 = cv2.inRange(hsv, hsv_min, hsv_max)
 
    # 赤色領域のマスク（255：赤色、0：赤色以外）
    mask = mask1 + mask2
 
    # マスキング処理
    masked_img = cv2.bitwise_and(img, img, mask=mask)
 
    return mask, masked_img
 
 
# 緑色の検出
def detect_green_color(img):
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
 
    # 緑色のHSVの値域1
    hsv_min = np.array([30, 64, 0])
    hsv_max = np.array([90, 255, 255])
 
    # 緑色領域のマスク（255：赤色、0：赤色以外）
    mask = cv2.inRange(hsv, hsv_min, hsv_max)
 
    # マスキング処理
    masked_img = cv2.bitwise_and(img, img, mask=mask)
 
    return mask, masked_img
 
 
# 青色の検出
def detect_blue_color(img):
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
 
    # 青色のHSVの値域1
    hsv_min = np.array([90, 64, 0])
    hsv_max = np.array([150, 255, 255])
 
    # 青色領域のマスク（255：赤色、0：赤色以外）
    mask = cv2.inRange(hsv, hsv_min, hsv_max)
 
    # マスキング処理
    masked_img = cv2.bitwise_and(img, img, mask=mask)
 
    return mask, masked_img
def ninesplit(image):
    h, w = image.shape[:2]
    n = 3  # 画像分割数
    y0 = int(h/n)
    x0 = int(w/n) 
    c = [image[x0*x:x0*(x+1), y0*y:y0*(y+1)] for x in range(n) for y in range(n)]
    p = []
    for i, img in enumerate(c):
        p.append(sum(sum(img)))
    img_x = np.vstack((np.hstack(p[0:3]),
                   np.hstack(p[3:6]),
                   np.hstack(p[6:9])
                  ))
    print(img_x)
    return img_x

# メイン関数
def main():
    # 初期化部
    # Telloクラスを使って，tellというインスタンス(実体)を作る
    tello = Tello(retry_count=1)    # 応答が来ないときのリトライ回数は1(デフォルトは3)
    tello.RESPONSE_TIMEOUT = 0.01   # コマンド応答のタイムアウトは短くした(デフォルトは7)

    # Telloへ接続
    tello.connect()

    # 画像転送を有効にする
    tello.streamoff()   # 誤動作防止の為、最初にOFFする
    tello.streamon()    # 画像転送をONに
    frame_read = tello.get_frame_read()     # 画像フレームを取得するBackgroundFrameReadクラスのインスタンスを作る

    current_time = time.time()  # 現在時刻の保存変数
    pre_time = current_time     # 5秒ごとの'command'送信のための時刻変数

    motor_on = False                    # モータON/OFFのフラグ
    camera_dir = Tello.CAMERA_FORWARD   # 前方/下方カメラの方向のフラグ

    time.sleep(0.5)     # 通信が安定するまでちょっと待つ
    # ループ部
    # Ctrl+cが押されるまでループ
    drone_state = "landing"
    try:
        # 永久ループで繰り返す
        while True:

            # (A) 画像取得
            
            image = frame_read.frame    # 映像を1フレーム取得しimage変数に格納

            # (B) 画像サイズ変更と、カメラ方向による回転
            small_image = cv2.resize(image, dsize=(480,360) )   # 画像サイズを半分に変更

            if camera_dir == Tello.CAMERA_DOWNWARD:     # 下向きカメラは画像の向きが90度ずれている
                small_image = cv2.rotate(small_image, cv2.ROTATE_90_CLOCKWISE)      # 90度回転して、画像の上を前方にする

            # (C) ここから画像処理

            # (X) ウィンドウに表示
            mask, mask_img = detect_red_color(small_image)
            
            cv2.imshow('OpenCV Window', mask)    # ウィンドウに表示するイメージを変えれば色々表示できる
            #nineimg     =    ninesplit(mask)
            if drone_state == "landing":
                tello.takeoff()
                drone_state = "takeoff"
            else:
                window_potision = np.argmax(mask)
                colore_intensity = np.max(mask)
                if colore_intensity == 0:
                    left_right = "right"
                    width = 15
                    if left_right == "rigth":
                        tello.move_right(width)
                        left_right = "left"
                        width += 5
                    elif left_right == "left":
                        tello.move_right(width)
                        left_right = "right"
                        width += 5      
                elif colore_intensity == 300:
                    tello.move_forward(20)
                if  window_potision[0] == 0:
                    tello.move_left(20)
                elif window_potision[0] == 2:
                    tello.move_right(20)
                else:
                    print(tello.get_current_state())
                if window_potision[1] == 0:
                    tello.move_up(20)
                elif window_potision[1] == 2:
                    tello.move_down(20)
                else:
                    print(tello.get_current_state())
                if  window_potision == (0,0):
                    tello.move_up(20)
                    tello.move_forward(20)
                    
            #key = cv2.waitKey(1) & 0xFF
    
    except( KeyboardInterrupt, SystemExit):    # Ctrl+cが押されたらループ脱出
        print( "Ctrl+c を検知" )

    # 終了処理部
    cv2.destroyAllWindows()                             # すべてのOpenCVウィンドウを消去
    tello.set_video_direction(Tello.CAMERA_FORWARD)     # カメラは前方に戻しておく
    tello.streamoff()                                   # 画像転送を終了(熱暴走防止)
    frame_read.stop()                                   # 画像受信スレッドを止める

    del tello.background_frame_read                    # フレーム受信のインスタンスを削除    
    del tello                                           # telloインスタンスを削除

# "python3 main_core.py"として実行された時だけ動く様にするおまじない処理
if __name__ == "__main__":      # importされると__name_に"__main__"は入らないので，pyファイルが実行されたのかimportされたのかを判断できる．
    main()    # メイン関数を実行
