from flask import Flask, render_template, request, send_file
from PIL import Image, ImageEnhance
import os
import uuid
from io import BytesIO
import numpy as np




app = Flask(__name__)
# Fotoğrafların yükleneceği klasörü ayarlayın
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def apply_filter(image, hue, saturation, lightness):
    img = Image.open(image)

    # Saturation ayarı
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(saturation)

    # Lightness ayarı
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(lightness)

    # HSV moduna dönüştürme
    img = img.convert('HSV')

    # Piksel verilerini al
    data = img.getdata()

    # Hue ayarı ve yeni piksel verilerini oluşturma
    newData = []
    for item in data:
        hue_value = item[0] + hue
        if hue_value > 255:
            hue_value = 255
        elif hue_value < 0:
            hue_value = 0

        newData.append( (hue_value, item[1], item[2]) )

    # Yeni piksel verilerini uygulama
    img.putdata(newData)

    # RGB moduna dönüştürme
    img = img.convert('RGB')

   # Geçici klasör oluşturma
    temp_path = 'static/temp/'
    os.makedirs(temp_path, exist_ok=True)

    # Benzersiz bir dosya adı oluşturma
    temp_filename = os.path.join(temp_path, f'filtered_image_{uuid.uuid4()}.jpg')

    # Görüntüyü kaydetme
    img.save(temp_filename)

    return temp_filename

@app.route('/', methods=['GET', 'POST'])
def index():
    save_path = None

    if request.method == 'POST':
        save_path = request.form.get('save_path')

    return render_template('index.html', save_path=save_path)

@app.route('/process', methods=['POST'])
def process():
    if 'image' not in request.files:
        return render_template('index.html', error='No image provided.')

    image = request.files['image']

    hue = float(request.form['hue'])
    saturation = float(request.form['saturation'])
    lightness = float(request.form['lightness'])

    # Filtreleme işlemini uygula ve filtrelenmiş dosya adını al
    temp_filename = apply_filter(image, hue, saturation, lightness)

    # Kullanıcının yüklediği fotoğrafı UPLOAD_FOLDER'a kaydet
    upload_filename = os.path.join(app.config['UPLOAD_FOLDER'], f'original_image_{uuid.uuid4()}.jpg')
    image.save(upload_filename)

    return render_template('index.html', result=temp_filename, original=upload_filename)





@app.route('/download')
def download():

    filtered_image_path = request.args.get('path', '')
    filename = request.args.get('filename', 'filtered_image.jpg')
    return send_file(filtered_image_path, as_attachment=True,
                     download_name=filename)

if __name__ == '__main__':
    app.run(debug=True)