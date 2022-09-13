#!/usr/bin/env python3
# -*- coding: utf-8 -*-q

from djitellopy import Tello    # DJITelloPyのTelloクラスをインポート
import time                     # time.sleepを使いたいので
import cv2                      # OpenCVを使うため
import numpy as np              # ラベリングにNumPyが必要なので

from window import window       #窓侵入関数
from linetrace import linetrace #ライントレース関数
from land import land           #着陸
from take_Ushape import take_Ushape #自動マッピング

#認識したい色を設定(R=赤, B=青, G=緑)
color_code = 'G'

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
    pr_time = current_time

    motor_on = False                    # モータON/OFFのフラグ
    camera_dir = Tello.CAMERA_FORWARD   # 前方/下方カメラの方向のフラグ

    # トラックバーを作るため，まず最初にウィンドウを生成
    cv2.namedWindow("OpenCV Window")

    # 自動モードフラグ(デフォルト)
    auto_mode = 'manual'

    #画像保存のためのパラメータ
    interval = 1.0              #撮影頻度
    imgnum = 0                  # auto_mode = 'mapping'
    scsnum = 0                  # key (space)
    mapnum = 0                  # key (x)

    map_area = 'big_table'

    #speed
    distance = 30
    #旋回角度
    degree = 30
    #昇降距離
    lift = 30

    #img　path
    img_path = '/Users/ryokokubun/Desktop/drone/'

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

            # (C) 自律モード

            #窓侵入
            if auto_mode == 'window':
                result_image, auto_mode = window(small_image, auto_mode, color_code)
                if auto_mode == 'room':
                    auto_mode = 'manual'
                    print(f'auto_mode = {auto_mode}')
                    print("======== Done Window =======")

            #3D Mapping
            elif auto_mode == 'mapping':
                # (interval) 秒おきに画像を習得する
                current_time = time.time()
                if current_time - pr_time > interval:
                    cv2.imwrite(img_path + 'map_img/tello' + str(imgnum) + ".jpg", image)
                    pr_time = current_time
                    imgnum += 1

            #自動移動マッピング
            elif auto_mode == 'auto_mapping':
                take_Ushape(tello)
                result_image = small_image

            #ライントレース
            elif auto_mode == 'linetrace':
                result_image, auto_mode = linetrace(small_image, auto_mode, color_code)
                if auto_mode == 'land':
                    print(f'auto_mode = {auto_mode}')
                    #auto_mode = 'manual'
                    print("======== Done linetrace =======")

            #着陸
            elif auto_mode == 'land':
                result_image, auto_mode = land(small_image, auto_mode, 'LR')
                if auto_mode == 'fin':
                    print(f'auto_mode = {auto_mode}')
                    auto_mode = 'manual'
                    print("======== Done land =======")

            elif auto_mode == 'manual':
                result_image = small_image

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
                tello.move_forward(distance)
            elif key == ord('s'):           # 後進 30cm
                tello.move_back(distance)
            elif key == ord('a'):           # 左移動 30cm
                tello.move_left(distance)
            elif key == ord('d'):           # 右移動 30cm
                tello.move_right(distance)
            elif key == ord('e'):           # 旋回-時計回り 30度
                tello.rotate_clockwise(degree)
            elif key == ord('q'):           # 旋回-反時計回り 30度
                tello.rotate_counter_clockwise(degree)
            elif key == ord('r'):           # 上昇 30cm
                tello.move_up(lift)
            elif key == ord('f'):           # 下降 30cm
                tello.move_down(lift)
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
                time.sleep(0.5)             # 映像が切り替わるまで少し待つ
            elif key == 32:                 #スペースキーでスクリーンショット
                cv2.imwrite(img_path + 'screen_shot/tello' + str(scsnum) + ".jpg", small_image)
                print('== Took a screenshot ==')
                scsnum += 1
            elif key == ord('n'):                 #nキーでスクリーンショット
                cv2.imwrite(img_path + 'map_shot/' + map_area +'/tello' + str(scsnum) + ".jpg", image)
                print(f'== Took a MapShot ({map_area}) ==')
                scsnum += 1
            elif key == ord('m'):                 #キーを押すごとにファイル保存場所を変更
                if map_area == 'big_table':
                    map_area = 'window_table'

                elif map_area == 'window_table':
                    map_area = 'entrance_table'

                elif map_area == 'entrance_table':
                    map_area = 'koshitu_1'

                elif map_area == 'koshitu_1':
                    map_area = 'koshitu_2'

                elif map_area == 'koshitu_2':
                    map_area = 'souko'

                elif map_area == 'souko':
                    map_area = 'DAA'

                elif map_area == 'DAA':
                    map_area = 'big_table'

                print(f'== Save file -> {map_area} ==')

            elif key == ord('g'):                # 移動距離を20->30->100とボタンを押すごとに変更(デフォルトは30)
                if distance == 20:
                    #画像取得のインターバルを速度に応じて変更
                    interval = 1
                    distance = 30
                elif distance == 30:
                    #画像取得のインターバルを速度に応じて変更
                    interval = 0.3
                    distance = 100
                elif distance == 100:
                    #画像取得のインターバルを速度に応じて変更
                    interval = 1.2
                    distance = 20
                print(f'distance={distance}, interval={interval}')
            elif key == ord('v'):           # 旋回角度を10->30->90とボタンを押すごとに変更(デフォルトは30)
                if degree == 10:
                    degree = 30
                elif degree == 30:
                    degree = 90
                elif degree == 90:
                    degree = 10
                print(f'degree={degree}')
            elif key == ord('b'):           # 昇降距離を30->50とボタンを押すごとに変更(デフォルトは30)
                if lift == 30:
                    lift = 50
                elif lift == 50:
                    lift = 30
                print(f'lift={lift}')

            # #お遊びフリップ関数
            # elif key == ord('u'):
            #     tello.flip_forward()
            # elif key == ord('j'):
            #     tello.flip_back()
            # elif key == ord('h'):
            #     tello.flip_left()
            # elif key == ord('k'):
            #     tello.flip_right()

            #自律モード
            elif key == ord('1'):
                tello.takeoff()
                time.sleep(5)     # 映像が切り替わるまで少し待つ
                tello.move_forward(100)
                #auto_mode = 'window'
            elif key == ord('2'):
                auto_mode = 'window'
                print(f'auto_mode={auto_mode}')
            elif key == ord('3'):
                auto_mode = 'mapping'
                print(f'auto_mode={auto_mode}')
            elif key == ord('4'):
                auto_mode = 'linetrace'
                print(f'auto_mode={auto_mode}')
            elif key == ord('5'):
                auto_mode = 'land'
                print(f'auto_mode={auto_mode}')
            elif key == ord('6'):
                auto_mode = 'auto_mapping'
                print(f'auto_mode={auto_mode}')

            elif key == ord('0'):
                tello.send_rc_control( 0, 0, 0, 0 )
                auto_mode = 'manual'                    # 追跡モードOFF
                print(f'auto_mode={auto_mode}')

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
    main()    # メイン関数を実行
