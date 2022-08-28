import cv2


def take_liner(tello,distance = 200, interval = 10):
    #右から左に動き、画像を取得する
    # : param object tello  : telloオブジェクト
    # : param int distance : 総移動距離(cm)
    # : param int interval : 何cm間隔で撮影を行うか

    # 画像転送を有効にする
    tello.streamoff()   # 誤動作防止の為、最初にOFFする
    tello.streamon()    # 画像転送をONに
    frame_read = tello.get_frame_read() 

    picnum = 0
    #高さを1.5mに設定
    height = tello.get_height()

    if height > 150:
        tello.move_down(height - 150)
    else :
        tello.move_up(150 - height)
    
    dis = 0

    #ループさせて、撮影
    while dis < distance :
        # (1) 画像取得
        image = frame_read.frame    # 映像を1フレーム取得しimage変数に格納

        # (2) 画像サイズ変更と、カメラ方向による回転
        small_image = cv2.resize(image, dsize=(480,360) )   # 画像サイズを半分に変更
        
        cv2.imwrite('./3drec/'+str(picnum)+".jpg", small_image)
        pic+=1

        tello.move_left(interval)
        dis += interval


    