for file in *.mp4; do
# echo $file
name=$(basename $file .mp4)
echo $name
# タイトルのフォルダを作成
mkdir $name
# mp4を移動＆名前変更
mv $file $name/input.mp4

# 変換実行
python ~/python/program/201214_mp4pdf/script/movie2pdf.py -dir ./$name/ -num_f 0.5
# OCR
ocrmypdf -l jpn --output-type pdfa --tesseract-pagesegmode 6 --sidecar $name/output.txt $name/slide.pdf $name/slide_ocr.pdf
# outputのslide.pdfのタイトル変更
mv $name/slide.pdf $name/$name.pdf
mv $name/slide_ocr.pdf $name/$name_ocr.pdf
done