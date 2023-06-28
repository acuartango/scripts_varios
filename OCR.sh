# convertir PDF a fotos
pdftoppm -png -r 300 23-06-23-\ Diario\ Vasco.pdf diariovasco

# OCR peor
cuneiform -l spa -f text -o diariovasco-49.png.output.txt diariovasco-49_resized.png

# Resize de fotos
convert diariovasco-49.png -resize 50% diariovasco-49_resized.png

# OCR mejor Tesseract
for i in `ls diariovasco*png`; do cuneiform -l spa -f text -o "${i}.output.txt" "$i" ; done
for i in `ls diariovasco*png`; do tesseract $i ${i}output2.txt -l spa --oem 1 --psm 3; done

