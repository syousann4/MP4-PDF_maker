#後から追加したウェブページで「PDF化＋OCR」ボタンなどが押された際に、Pythonからこのスクリプトを叩けるようにするためのコード
import subprocess

def run_ocr_script(target_dir):
    # .sh スクリプトを呼び出す
    result = subprocess.run(
        ["/bin/bash", "./movie2pdf_folder_ocr.sh", target_dir],
        capture_output=True,
        text=True
    )
    return result.stdout