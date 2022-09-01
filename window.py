#!/usr/bin/env python3
# -*- coding: utf-8 -*-q

from djitellopy import Tello    # DJITelloPyのTelloクラスをインポート
import time                     # time.sleepを使いたいので
import cv2                      # OpenCVを使うため
import numpy as np              # ラベリングにNumPyが必要なので

from hsvColor import hsv_color  #設定された色を取得するため

# Telloクラスを使って，tellというインスタンス(実体)を作る
tello = Tello(retry_count=1)

#####################   window()   ############################
#
#   引数
#   small_image:    telloが取得したオリジナル画像（size 480*360）
#   auto_mode:      telloの現在の状態
#   color_code:     認識したい色(R=赤, B=青, G=緑)
#
#   戻り値
#   result_image:   画像処理後の画像
#   auto_mode:      telloの現在の状態（完了したら状態は'room'
#                                    になります)
#
###############################################################

# 安定性フラグ
stable = 0          #上下、左右について安定性を維持している時間（フレーム数)
b_stable = 0        #マーカーとの距離について安定性を維持している時間（フレーム数)

def window(small_image, auto_mode=None, color_code='R'):

    global stable, b_stable

    bgr_image = small_image                              # 窓を認識するまで広い視野で確認する
    hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)  # BGR画像 -> HSV画像

    #認識する色のhsvを取得（デフォルトは赤）
    hsv_min, hsv_max = hsv_color(color_code)

    # inRange関数で範囲指定２値化
    bin_image = cv2.inRange(hsv_image, hsv_min, hsv_max)        # HSV画像なのでタプルもHSV並び
    kernel = np.ones((15,15),np.uint8)  # 15x15で膨張させる
    bin_image = cv2.dilate(bin_image,kernel,iterations = 1)    # 膨張してラベルを一つにする

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

        #侵入位置移動モード
        if auto_mode == 'window':
            # a:左右
            # b:前後
            # c:上下
            # d:旋回
            a = b = c = d = 0

            ##########  左右  ##########
            # 制御式
            ax = 0.3 * (240 - mx)

            # 左右移動の不感帯を設定
            a = 0.0 if abs(ax) < 10.0 else ax   # ±30未満ならゼロにする

            # 左右移動のソフトウェアリミッタ(±20を超えないように)
            a =  20 if a >  20.0 else a
            a = -20 if a < -20.0 else a

            #マーカーに近づくとブレが大きくなるためリミッタを狭める
            if stable > 200:
                a =  10 if a >  10.0 else a
                a = -10 if a < -10.0 else a

            a = -a   # 左右方向が逆だったので符号を反転
            #print('ax=%f'%(ax) )

            ##########  前後  ##########
            if stable > 200:                       #マーカーを中心に捉えていたら前に移動
                #stable = 0                         #移動してもマーカーを中心に捉えるようにする
                # 制御式
                bx = 0.003 * (30000 - s)           #期待する面積→45000

                # 前後移動の不感帯を設定
                b = 0.0 if abs(bx) < 9.0 else bx   # 面積差が±3000未満ならゼロにする

                # 前後移動のソフトウェアリミッタ(±10を超えないように)
                b =  10 if b >  10.0 else b
                b = -10 if b < -10.0 else b

                #print(f'b={b}')

            ##########  上下  ##########
            # 制御式
            cx = 0.3 * (180 - my)

            # 上下移動の不感帯を設定
            c = 0.0 if abs(cx) < 10.0 else cx   # ±30未満ならゼロにする

            # 上下移動のソフトウェアリミッタ(±20を超えないように)
            c =  20 if c >  20.0 else c
            c = -20 if c < -20.0 else c

            #マーカーに近づくとブレが大きくなるためリミッタを狭める
            if stable > 200:
                c =  10 if c >  10.0 else c
                c = -10 if c < -10.0 else c

            #print('cx=%f'%(cx) )

            """
            ##########  旋回(ターゲットを画面の中央に捉える機能)  ##########
            # 制御式(ゲインは低めの0.3)
            dx = 0.4 * (240 - mx)       # 画面中心との差分

            # 旋回方向の不感帯を設定
            d = 0.0 if abs(dx) < 10.0 else dx   # ±50未満ならゼロにする

            # 旋回方向のソフトウェアリミッタ(±100を超えないように)
            d =  100 if d >  100.0 else d
            d = -100 if d < -100.0 else d

            d = -d   # 旋回方向が逆だったので符号を反転
            print('dx=%f'%(dx) )
            """

            #マーカーを中心に捉えていたら安定ポイント+1
            if (a == 0 and c == 0):
                stable += 1

            #窓に侵入できる位置に安定していたらb安定ポイント+1
            if (stable > 200 and b == 0):
                b_stable += 1

            #窓に侵入できる位置まで来たら侵入モードに移行
            if b_stable > 50:
                auto_mode = 'invasion'

            print(f'stable = {stable}, b_stable = {b_stable}')
            tello.send_rc_control( int(a), int(b), int(c), int(d) )

    #窓侵入モード
    if auto_mode == 'invasion':
        tello.move_up(30)
        time.sleep(3)
        tello.move_forward(100)
        print(f'===== auto_mode({auto_mode}) done =====')
        auto_mode = 'room'

    return result_image, auto_mode

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

    # トラックバーを作るため，まず最初にウィンドウを生成
    cv2.namedWindow("OpenCV Window")

    # 自動モードフラグ
    auto_mode = 'manual'

    time.sleep(0.5)     # 通信が安定するまでちょっと待つ

    # ループ部
    # Ctrl+cが押されるまでループ
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

            #窓侵入
            result_image, auto_mode = window(small_image, auto_mode, color_code)
            if auto_mode == 'room':
                print("======== Done Window =======")
                auto_mode = 'manual'

            # (X) ウィンドウに表示
            cv2.imshow('OpenCV Window', result_image)    # ウィンドウに表示するイメージを変えれば色々表示できる
            #cv2.imshow('Binary Image', bin_image)
            cv2.imshow('defo Image', small_image)

            # (Y) OpenCVウィンドウでキー入力を1ms待つ
            key = cv2.waitKey(1) & 0xFF
            if key == 27:                   # key が27(ESC)だったらwhileループを脱出，プログラム終了
                break
            elif key == ord('t'):           # 離陸
                tello.takeoff()
            elif key == ord('l'):           # 着陸
                tello.send_rc_control( 0, 0, 0, 0 )
                tello.land()
            elif key == ord('w'):           # 前進 30cm
                tello.move_forward(30)
            elif key == ord('s'):           # 後進 30cm
                tello.move_back(30)
            elif key == ord('a'):           # 左移動 30cm
                tello.move_left(30)
            elif key == ord('d'):           # 右移動 30cm
                tello.move_right(30)
            elif key == ord('e'):           # 旋回-時計回り 30度
                tello.rotate_clockwise(30)
            elif key == ord('q'):           # 旋回-反時計回り 30度
                tello.rotate_counter_clockwise(30)
            elif key == ord('r'):           # 上昇 30cm
                tello.move_up(30)
            elif key == ord('f'):           # 下降 30cm
                tello.move_down(30)
            elif key == ord('p'):           # ステータスをprintする
                print(tello.get_current_state())
            elif key == ord('m'):           # モータ始動/停止を切り替え
                if motor_on == False:       # 停止中なら始動
                    tello.turn_motor_on()
                    motor_on = True
                else:                       # 回転中なら停止
                    tello.turn_motor_off()
                    motor_on = False
            elif key == ord('c'):           # カメラの前方/下方の切り替え
                if camera_dir == Tello.CAMERA_FORWARD:     # 前方なら下方へ変更
                    tello.set_video_direction(Tello.CAMERA_DOWNWARD)
                    camera_dir = Tello.CAMERA_DOWNWARD     # フラグ変更
                else:                                      # 下方なら前方へ変更
                    tello.set_video_direction(Tello.CAMERA_FORWARD)
                    camera_dir = Tello.CAMERA_FORWARD      # フラグ変更
                time.sleep(0.5)     # 映像が切り替わるまで少し待つ
            elif key == ord('1'):
                auto_mode = 'window'                    # 追跡モードON
            elif key == ord('0'):
                tello.send_rc_control( 0, 0, 0, 0 )
                auto_mode = 'manual'                    # 追跡モードOFF

            # (Z) 10秒おきに'command'を送って、死活チェックを通す
            current_time = time.time()                          # 現在時刻を取得
            if current_time - pre_time > 10.0 :                 # 前回時刻から10秒以上経過しているか？
                tello.send_command_without_return('command')    # 'command'送信
                pre_time = current_time                         # 前回時刻を更新

    except( KeyboardInterrupt, SystemExit):    # Ctrl+cが押されたらループ脱出
        print( "Ctrl+c を検知" )

    # 終了処理部
    tello.send_rc_control( 0, 0, 0, 0 )
    cv2.destroyAllWindows()                             # すべてのOpenCVウィンドウを消去
    tello.set_video_direction(Tello.CAMERA_FORWARD)     # カメラは前方に戻しておく
    tello.streamoff()                                   # 画像転送を終了(熱暴走防止)
    frame_read.stop()                                   # 画像受信スレッドを止める

    del tello.background_frame_read                    # フレーム受信のインスタンスを削除
    del tello                                           # telloインスタンスを削除

# "python3 main_linetrace.py"として実行された時だけ動く様にするおまじない処理
if __name__ == "__main__":      # importされると__name_に"__main__"は入らないので，pyファイルが実行されたのかimportされたのかを判断できる．
    #認識したい色を設定(R=赤, B=青, G=緑)
    color_code = 'R'
    main()    # メイン関数を実行
