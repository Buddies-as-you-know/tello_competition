import os
import time

import cv2
import numpy as np
from djitellopy import Tello


def detect_color(img):
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 赤色のHSVの値域1
    hsv_min = np.array([0, 0, 0])
    hsv_max = np.array([255, 64, 255])
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


def ninesplit(image):
    h, w = image.shape[:2]
    n = 3  # 画像分割数
    y0 = int(h / n)
    x0 = int(w / n)
    c = [
        image[x0 * x : x0 * (x + 1), y0 * y : y0 * (y + 1)]
        for x in range(n)
        for y in range(n)
    ]
    p = []
    for i, img in enumerate(c):
        cv2.imwrite(os.path.join("./", "{}.jpg".format(i)), img)
    for i, img in enumerate(c):
        p.append(sum(sum(img)))
    img_x = np.vstack((np.hstack(p[0:3]), np.hstack(p[3:6]), np.hstack(p[6:9])))
    print(img_x)
    return img_x


class Land:
    def judge_bottom_white(self) -> str:
        max_judge = [sum(self.nineimg[0]), sum(self.nineimg[1]), sum(self.nineimg[2])]
        forward_down_judge = max_judge.index(max(max_judge))
        if forward_down_judge == 2:
            return "down"
        else:
            return "forward"

    def move_tello_from_judge_bottom_white(self, nineimg) -> None:
        self.nineimg = nineimg
        down_or_forward = self.judge_bottom_white()
        if down_or_forward == "down":
            pass
            # telloを下げる。
        else:
            pass
            # tello前に進める。


if __name__ == "__main__":

    tello = Tello(retry_count=1)  # 応答が来ないときのリトライ回数は1(デフォルトは3)
    tello.RESPONSE_TIMEOUT = 0.01  # コマンド応答のタイムアウトは短くした(デフォルトは7)

    # Telloへ接続
    tello.connect()

    # 画像転送を有効にする
    tello.streamoff()  # 誤動作防止の為、最初にOFFする
    tello.streamon()  # 画像転送をONに
    frame_read = tello.get_frame_read()  # 画像フレームを取得するBackgroundFrameReadクラスのインスタンスを作る

    current_time = time.time()  # 現在時刻の保存変数
    pre_time = current_time  # 5秒ごとの'command'送信のための時刻変数

    motor_on = False  # モータON/OFFのフラグ
    camera_dir = Tello.CAMERA_FORWARD  # 前方/下方カメラの方向のフラグ

    time.sleep(0.5)  # 通信が安定するまでちょっと待つ
    # ループ部
    # Ctrl+cが押されるまでループ
    try:
        # 永久ループで繰り返す
        while True:

            # (A) 画像取得

            image = frame_read.frame  # 映像を1フレーム取得しimage変数に格納

            # (B) 画像サイズ変更と、カメラ方向による回転
            small_image = cv2.resize(image, dsize=(480, 360))  # 画像サイズを半分に変更

            if camera_dir == Tello.CAMERA_DOWNWARD:  # 下向きカメラは画像の向きが90度ずれている
                small_image = cv2.rotate(
                    small_image, cv2.ROTATE_90_CLOCKWISE
                )  # 90度回転して、画像の上を前方にする
            """もし着陸になったら"""
            land = Land()
            mask, mask_img = detect_color(small_image)
            nine_image = ninesplit(mask)
            land.move_tello_from_judge_bottom_white(nineimg=nine_image)
    except (KeyboardInterrupt, SystemExit):  # Ctrl+cが押されたらループ脱出
        print("Ctrl+c を検知")

    # 終了処理部
    cv2.destroyAllWindows()  # すべてのOpenCVウィンドウを消去
    tello.set_video_direction(Tello.CAMERA_FORWARD)  # カメラは前方に戻しておく
    tello.streamoff()  # 画像転送を終了(熱暴走防止)
    frame_read.stop()  # 画像受信スレッドを止める

    del tello.background_frame_read  # フレーム受信のインスタンスを削除
    del tello
