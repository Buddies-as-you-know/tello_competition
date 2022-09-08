import os

import cv2
import numpy as np


def detect_red_color(img):
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
    y0 = int(h/n)
    x0 = int(w/n) 
    c = [image[x0*x:x0*(x+1), y0*y:y0*(y+1)] for x in range(n) for y in range(n)]
    p = []
    for i, img in enumerate(c):
      cv2.imwrite(os.path.join('./', '{}.jpg'.format(i)), img)
    for i, img in enumerate(c):
        p.append(sum(sum(img)))
    img_x = np.vstack((np.hstack(p[0:3]),
                   np.hstack(p[3:6]),
                   np.hstack(p[6:9])
                  ))
    print(img_x)
    return img_x

class land:
  def __init__(self,nineimg,state) -> None:
    self.state = state

  def judge_bottom_white(self) -> str:
      max_judge = [sum(self.nineimg[0]), sum(self.nineimg[1]), sum(self.nineimg[2])]
      forward_down_judge = max_judge.index(max(max_judge))
      if  forward_down_judge == 2:
        return 'down'
      else:
        return 'forward'
  def move_tello_from_judge_bottom_white(self,nineimg) -> None:
    while "To stop":
      self.nineimg = nineimg

      down_or_forward = self.judge_bottom_white()
      if down_or_forward == 'down':
        #telloを下げる。
      else:
        #tello前に進める。
