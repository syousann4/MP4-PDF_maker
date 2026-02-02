FROM ubuntu:24.04

# 環境変数
ENV DEBIAN_FRONTEND=noninteractive

# 必要なシステムパッケージのインストール
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    libglu1-mesa \
    curl \
    # 追加: Tesseract OCRのインストールここから
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-jpn \ 
    #ここまで
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python依存ライブラリのインストール
# yt-dlp, opencv-python, img2pdf, flask/fastapiなど
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages

COPY . .

#後から追加したスクリプト実行のための追加部分
# スクリプトをコピー
COPY movie2pdf_folder_ocr.sh /app/

# 実行権限を付与
RUN chmod +x /app/movie2pdf_folder_ocr.sh

CMD ["python3", "app.py"]