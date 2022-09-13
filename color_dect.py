#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2                      # OpenCVを使うため
import numpy as np              # ラベリングにNumPyが必要なので

# トラックバーのコールバック関数は何もしない空の関数
def nothing(x):
    pass        # passは何もしないという命令

im = cv2.imread('/Users/ryokokubun/Desktop/line.jpg')

cv2.namedWindow("OpenCV Window")

# トラックバーの生成
cv2.createTrackbar("H_min", "OpenCV Window", 0, 179, nothing)       # Hueの最大値は179
cv2.createTrackbar("H_max", "OpenCV Window", 179, 179, nothing)
cv2.createTrackbar("S_min", "OpenCV Window", 0, 255, nothing)
cv2.createTrackbar("S_max", "OpenCV Window", 255, 255, nothing)
cv2.createTrackbar("V_min", "OpenCV Window", 0, 255, nothing)
cv2.createTrackbar("V_max", "OpenCV Window", 255, 255, nothing)

try:

    while True:

        small_image = cv2.resize(im, dsize=(480,360) )   # 画像サイズを半分に変更
        hsv_image = cv2.cvtColor(small_image, cv2.COLOR_BGR2HSV)  # BGR画像 -> HSV画像

        # トラックバーの値を取る
        h_min = cv2.getTrackbarPos("H_min", "OpenCV Window")
        h_max = cv2.getTrackbarPos("H_max", "OpenCV Window")
        s_min = cv2.getTrackbarPos("S_min", "OpenCV Window")
        s_max = cv2.getTrackbarPos("S_max", "OpenCV Window")
        v_min = cv2.getTrackbarPos("V_min", "OpenCV Window")
        v_max = cv2.getTrackbarPos("V_max", "OpenCV Window")

        print("=============================")
        print(f'h_min={h_min}, h_max={h_max}')
        print(f's_min={s_min}, s_max={s_max}')
        print(f'v_min={v_min}, v_max={v_max}')
        print("=============================")

        # inRange関数で範囲指定２値化
        bin_image = cv2.inRange(hsv_image, (h_min, s_min, v_min), (h_max, s_max, v_max)) # HSV画像なのでタプルもHSV並び

        # bitwise_andで元画像にマスクをかける -> マスクされた部分の色だけ残る
        result_image = cv2.bitwise_and(hsv_image, hsv_image, mask=bin_image)   # HSV画像 AND HSV画像 なので，自分自身とのANDは何も変化しない->マスクだけ効かせる

        # 面積・重心計算付きのラベリング処理を行う
        num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(bin_image)

        # 最大のラベルは画面全体を覆う黒なので不要．データを削除
        num_labels = num_labels - 1
        stats = np.delete(stats, 0, 0)
        center = np.delete(center, 0, 0)

        if num_labels >= 1:
            # 面積最大のインデックスを取得
            max_index = np.argmax(stats[:,4])
            #print max_index

            # 面積最大のラベルのx,y,w,h,面積s,重心位置mx,myを得る
            x = stats[max_index][0]
            y = stats[max_index][1]
            w = stats[max_index][2]
            h = stats[max_index][3]
            s = stats[max_index][4]
            mx = int(center[max_index][0])
            my = int(center[max_index][1])
            #print("(x,y)=%d,%d (w,h)=%d,%d s=%d (mx,my)=%d,%d"%(x, y, w, h, s, mx, my) )

            # ラベルを囲うバウンディングボックスを描画
            cv2.rectangle(result_image, (x, y), (x+w, y+h), (255, 0, 255))

            # 重心位置の座標と面積を表示
            cv2.putText(result_image, "%d,%d"%(mx,my), (x-15, y+h+15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))
            cv2.putText(result_image, "%d"%(s), (x, y+h+30), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))

            # (4) ウィンドウに表示
            cv2.imshow('OpenCV Window', result_image)    # ウィンドウに表示するイメージを変えれば色々表示できる
            cv2.imshow('Binary Image', bin_image)

            key = cv2.waitKey(1) & 0xFF

except( KeyboardInterrupt, SystemExit):    # Ctrl+cが押されたらループ脱出
    print( "Ctrl+c を検知" )

# 終了処理部
cv2.destroyAllWindows()                             # すべてのOpenCVウィンドウを消去
