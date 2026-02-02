# # 使い方
# # python movie2pdf.py -dir 実行フォルダのパス

# import argparse
# import subprocess
# import glob
# import cv2
# import shutil
# import os
# # pdfへ変換
# from PIL import Image
# import img2pdf
# # pdfをまとめる
# import re
# import PyPDF2
# from send2trash import send2trash



# # コマンドライン引数の取得
# parser = argparse.ArgumentParser()
# parser.add_argument('-dir')
# parser.add_argument('-num_f', default=0.5)
# args = parser.parse_args()

# base_dir = args.dir
# num_frames = args.num_f
# # floatに変換
# num_frames = float(num_frames)

# # avi→mp4へ変換
# input_avi = base_dir + "input.avi"
# if os.path.exists(input_avi):
#     cmd = 'ffmpeg -i {0} -vcodec libx265 -tag:v hvc1 {1}input.mp4'.format(
#         input_avi, base_dir)
#     subprocess.run(cmd, shell=True)
#     print("Done! - avi2mp4")
# else:
#     print("Not Avi file")

# # mp4→連番のpng
# input_mp4 = base_dir + "input.mp4"
# os.makedirs(base_dir + "photo")
# # 5秒に1枚のpngへ
# # -rは1秒あたりのコマ数
# cmd = 'ffmpeg -i {0} -vcodec png -r {1} {2}photo/%05d.png'.format(
#     input_mp4, num_frames, base_dir)
# subprocess.run(cmd, shell=True)
# print("Done! - mp4topng")

# # 連番png→重複除いてpdf作成
# # ２値化


# def binarization(img, threshold=100):
#     ret, img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
#     return img

# # 関数
# # 差分を数値化


# def getDiff(path1, path2):
#     # 画像の読み込み
#     img1 = cv2.imread(path1)
#     img2 = cv2.imread(path2)
#     # グレースケール変換
#     img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
#     img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
#     # 差分取得
#     mask = cv2.absdiff(img1, img2)
#     # ２値化
#     mask = binarization(mask)
#     return cv2.countNonZero(mask)  # 白の要素数


# # 重複を除く
# files = glob.glob(base_dir + "photo/*.png")
# files = sorted(files)

# list_frame_save = []  # 保存する画像のリスト
# threshold = 10000  # しきい値

# while True:
#     if len(files) > 1:
#         diff = getDiff(files[0], files[1])
#         if diff == 0:
#             files.remove(files[1])
#         elif 0 < diff < threshold:
#             files.remove(files[1])
#         else:
#             print(files[0])
#             list_frame_save.append(files[0])
#             files.remove(files[0])

#     else:
#         break

# list_frame_save = list_frame_save + files

# # ファイルのコピー
# os.makedirs(base_dir + "save")
# for i in list_frame_save:
#     file_name = os.path.basename(i)
#     shutil.copyfile(i, base_dir + "save/" + file_name)

# # pdfへ変換
# # png→jpg
# # 保存先のディレクトリを作成
# os.makedirs(base_dir + "jpg")

# list_png = list_frame_save
# for i in list_png:
#     name, ext = os.path.splitext(i)
#     name_png = name.split("/")[-1] + ".jpg"
#     # 変換
#     im = Image.open(i)
#     rgb_im = im.convert('RGB')
#     rgb_im.save(base_dir + "jpg/" + name_png)

# # jpg→pdf
# path_jpg = base_dir + "jpg/*.jpg"
# list_jpg = glob.glob(path_jpg)
# # 保存先のディレクトリを作成
# os.makedirs(base_dir + "pdf")

# for i in list_jpg:
#     name, ext = os.path.splitext(i)
#     name_pdf = name.split("/")[-1] + ".pdf"
#     # 変換
#     # Pillowモジュールを使用し画像の読み込み
#     img = Image.open(i)
#     # 画像→pdfファイルに変換
#     cov_pdf = img2pdf.convert(i)
#     # pdfファイルを読み込み（pdf_nameで指定したpdfがない場合、pdf_nameをファイル名として新規にpdfファイルを作成）
#     file = open(base_dir + "pdf/" + name_pdf, "wb")
#     # pdfファイルを書き込み
#     file.write(cov_pdf)

#     # 開いているファイルを閉じる
#     img.close()
#     file.close()

# # 複数のpdfファイルを結合する
# pdf_path = base_dir + "pdf/"

# merge = PyPDF2.PdfFileMerger()
# for j in sorted(os.listdir(pdf_path), key=lambda s: int(re.search(r'\d+', s).group())):
#     merge.append(pdf_path + "/" + j)
# merge.write(base_dir + 'slide.pdf')
# merge.close()

# # フォルダとファイルを削除
# shutil.rmtree(base_dir + "jpg")
# shutil.rmtree(base_dir + "pdf")
# send2trash(base_dir + "photo")  # photoフォルダはごみ箱へ移動
# if os.path.exists(input_avi):
#     send2trash(base_dir + "input.avi")
# else:
#     pass

# print("Done! All")


import os
import subprocess
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__)
UPLOAD_FOLDER = 'work_dir'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        # ユニークな作業用IDを作成
        job_id = str(uuid.uuid4())
        job_path = os.path.join(UPLOAD_FOLDER, job_id)
        os.makedirs(job_path, exist_ok=True)

        url = request.form.get('url')
        file = request.files.get('file')
        run_ocr = request.form.get('runOcr') == 'on'
        video_file = os.path.join(job_path, "input.mp4")

        # 1. 動画の取得
        if url:
            ydl_opts = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best', 'outtmpl': video_file}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        elif file:
            file.save(video_file)
        else:
            return jsonify({'success': False, 'error': '動画が指定されていません'})

        # 2. movie2pdf.py の実行 (例: -dir オプションで作業ディレクトリを指定)
        # ※movie2pdf.pyの仕様に合わせてコマンド引数を調整してください
        subprocess.run(["python3", "movie2pdf.py", "-dir", job_path], check=True)

        # 3. OCRスクリプトの実行（チェックがある場合）
        if run_ocr:
            subprocess.run(["/bin/bash", "./movie2pdf_folder_ocr.sh", job_path], check=True)

        # 4. 生成されたPDFを探す（仮にoutput.pdfとする）
        pdf_filename = "output.pdf" # スクリプトの出力名に合わせて変更
        
        return jsonify({
            'success': True, 
            'pdf_url': f'/download/{job_id}/{pdf_filename}'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<job_id>/<filename>')
def download(job_id, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, job_id), filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)