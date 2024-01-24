# Flask kütüphanesini içe aktarın
from flask import Flask, render_template, request, send_file, redirect, url_for
import os
from PIL import Image, ImageOps
import numpy as np
from io import BytesIO

# Flask uygulamanınızı oluşturun ve şablon klasörünü ayarlayın
app = Flask(__name__, template_folder="templates")

# Fotoğrafların yükleneceği klasörü ayarlayın
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ana sayfayı işleyen endpoint
@app.route('/')
def upload_file():
    # Kullanıcıya Renk.html şablonunu gönderin
    return render_template('Renk.html')

# Fotoğraf yükleme işlemini gerçekleştiren endpoint
@app.route('/upload', methods=['POST'])
def upload():
    if 'photo' not in request.files:
        return 'No file part'
    photo = request.files['photo']
    if photo.filename == '':
        return 'No selected file'

    # Yüklenen fotoğrafı kaydedin
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
    photo.save(photo_path)

    # Kullanıcıyı fotoğrafı işlemek için başka bir sayfaya yönlendirin
    return redirect(url_for('process_image', photo_path=photo_path))

# Fotoğraf işleme sayfasını işleyen endpoint
@app.route('/process_image')
def process_image():
    photo_path = request.args.get('photo_path')

    # Kullanıcıya farkli_sayfa.html şablonunu ve işlenmiş fotoğrafı gönderin
    return render_template('Renk.html', photo_path=photo_path)

# Filtrelenmiş fotoğrafı indirme işlemini gerçekleştiren endpoint
@app.route('/download')
def download():
    photo_path = request.args.get('photo_path')
    if photo_path:
        image = Image.open(photo_path)

        # Filtrelenmiş fotoğrafı kullanıcıya sunun
        return send_file(
            BytesIO(np.array(ImageOps.exif_transpose(image).convert("RGB"))),
            as_attachment=True,
            download_name='filtered_image.jpg',
            mimetype='image/jpeg'
        )

# Flask uygulamanınızı çalıştırın
if __name__ == '__main__':
    app.run(debug=True)