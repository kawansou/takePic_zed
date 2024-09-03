import os
# opencvをインポートする前にこの処理を加えると起動が早くなる
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
import time
import beep
import sys
import shutil
import pyzed.sl as sl

# ZEDカメラを初期化
zed = sl.Camera()

# カメラの設定
init_params = sl.InitParameters()
init_params.camera_resolution = sl.RESOLUTION.HD1080
init_params.coordinate_units = sl.UNIT.MILLIMETER

# カメラをオープン
err = zed.open(init_params)
if err != sl.ERROR_CODE.SUCCESS:
    print(f"Failed to open ZED camera: {err}")
    exit(1)


# 変数設定
FOLDER_NAME = "./path_to_folder/" # 保存先ディレクトリ
FILE_NAME = "filename_" # ファイル名（共通）
EXTENSION = ".jpg"
SLEEP_SEC = 1 # 撮影間隔[sec]
SHOW_WIN_SCALE = 0.5 # 表示ウィンドウの倍率
FOCUS_VAL = 120  # フォーカス値
PROP_VAL = -4  # 露光

counter = 0 # ファイル名（番号）

# 初期設定画面
counter = int(input("Please input first file no: "))
cmd = input("Are you sure start process? (y/n): ")
print("\n")
print("When you quit process, please put control+c", file=sys.stderr)



# 点群用のMatを作成
image_color = sl.Mat()


res = sl.Resolution()
# res.width = 1280
# res.height = 720
res.width = 1920
res.height = 1080

cv2.namedWindow("camera", cv2.WINDOW_NORMAL)

# フォルダがなかったら作成
os.makedirs(FOLDER_NAME, exist_ok=True)

# 繰り返し処理
while cmd == "y":
    # ZEDから新しいフレームを取得
    if zed.grab() == sl.ERROR_CODE.SUCCESS:

        try:

            # ファイル名生成
            fileName = FOLDER_NAME + FILE_NAME + str(counter) + EXTENSION

            # カメラ画像取得
            zed.retrieve_image(image_color, sl.VIEW.LEFT)  # 色情報を取得
            img = image_color.get_data()

            # 画像を表示
            frame = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
            time.sleep(0.1)

            # 画像保存
            cv2.imwrite(fileName, frame)

            # 表示用に画像サイズを変更
            edt_h = int(frame.shape[0]*SHOW_WIN_SCALE)
            edt_w = int(frame.shape[1]*SHOW_WIN_SCALE)
            cv2.resizeWindow("camera", edt_w, edt_h) 

            # カメラ画像出力
            cv2.imshow('camera', frame)
            key = cv2.waitKey(10)
            
            # 画像保存が完了したらビープ音を鳴らす
            beep.beepOn(1500, 500)
            print(fileName + " was saved", file=sys.stderr)
            
            # 一定時間停止
            time.sleep(SLEEP_SEC)

            counter += 1

        # control+cが入力されたら処理を終了
        except KeyboardInterrupt:
            print("receive control+c\n")
            cmd = "n"

# メモリ解放
# ZEDをクローズ
zed.close()
cv2.destroyAllWindows()

# キャッシュファイル削除
shutil.rmtree('./__pycache__/')

print("Finish process")