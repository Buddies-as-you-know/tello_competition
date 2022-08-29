from djitellopy import Tello    # DJITelloPyのTelloクラスをインポート
import cv2                      # OpenCVを使うため
import numpy as np              # ラベリングにNumPyが必要なので

def linetrace():
    # (C) ここから画像処理
    bgr_image = small_image[250:359,0:479]              # 注目する領域(ROI)を(0,250)-(479,359)で切り取る
    hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)  # BGR画像 -> HSV画像

    # トラックバーの値を取る
    h_min = cv2.getTrackbarPos("H_min", "OpenCV Window")
    h_max = cv2.getTrackbarPos("H_max", "OpenCV Window")
    s_min = cv2.getTrackbarPos("S_min", "OpenCV Window")
    s_max = cv2.getTrackbarPos("S_max", "OpenCV Window")
    v_min = cv2.getTrackbarPos("V_min", "OpenCV Window")
    v_max = cv2.getTrackbarPos("V_max", "OpenCV Window")

    # inRange関数で範囲指定２値化
    bin_image = cv2.inRange(hsv_image, (h_min, s_min, v_min), (h_max, s_max, v_max)) # HSV画像なのでタプルもHSV並び
    kernel = np.ones((15,15),np.uint8)  # 15x15で膨張させる
    bin_image = cv2.dilate(bin_image,kernel,iterations = 1)    # 膨張して虎ロープをつなげる

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

        if auto_mode == 1:
            a = b = c = d = 0
            b=30

            # 制御式(ゲインは低めの0.3)
            dx = 0.4 * (240 - mx)       # 画面中心との差分

            # 旋回方向の不感帯を設定
            d = 0.0 if abs(dx) < 10.0 else dx   # ±50未満ならゼロにする

            # 旋回方向のソフトウェアリミッタ(±100を超えないように)
            d =  100 if d >  100.0 else d
            d = -100 if d < -100.0 else d

            d = -d   # 旋回方向が逆だったので符号を反転

            print('dx=%f'%(dx) )
            tello.send_rc_control( int(a), int(b), int(c), int(d) )

    return flag
