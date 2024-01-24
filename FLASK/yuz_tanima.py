from flask import Flask, render_template, request, jsonify, send_file
import os
import cv2
import face_recognition
import numpy as np
import pickle
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'static'
KNOWN_FACES_FILE = 'know_facess.dat'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

thresh = 0.5

def augment_image(image):
    images = []
    images.append(image)
    return images

def clean_filename(name):
    cleaned_name = ''.join(c if c.isalnum() or c in ['.', '_', '-'] else '_' for c in name)
    return cleaned_name

def save_new_face(unknown_image, name, known_face_encodings, known_face_names, folder_name):
    folder_path = os.path.join('Yüzler', folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    width, height = 100, 90
    img_resized = cv2.resize(unknown_image, (width, height), interpolation=cv2.INTER_LINEAR)
    augmented_images = augment_image(img_resized)

    for i, aug_img in enumerate(augmented_images):
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(folder_path, f"{name}_{current_time}_{i}.jpg")
        cv2.imwrite(file_path, aug_img)

        face_encodings = face_recognition.face_encodings(aug_img)
        if face_encodings:
            new_encoding = face_encodings[0]
            known_face_encodings.append(new_encoding)
            known_face_names.append(name)

    with open(KNOWN_FACES_FILE, 'wb') as face_data_file:
        pickle.dump((known_face_encodings, known_face_names), face_data_file)

    return known_face_encodings, known_face_names

def load_known_faces():
    try:
        with open(KNOWN_FACES_FILE, 'rb') as face_data_file:
            known_face_encodings, known_face_names = pickle.load(face_data_file)
    except FileNotFoundError:
        known_face_encodings, known_face_names = [], []

    return known_face_encodings, known_face_names

def recognize_faces(unknown_image, known_face_encodings, known_face_names, threshold=0.5):
    try:
        unknown_locations = face_recognition.face_locations(unknown_image)
        unknown_encodings = face_recognition.face_encodings(unknown_image, unknown_locations)

        recognized_faces = []

        for (top, right, bottom, left), unknown_encoding in zip(unknown_locations, unknown_encodings):
            distances = face_recognition.face_distance(known_face_encodings, unknown_encoding)
            best_match_index = np.argmin(distances)
            name = "Bilinmiyor" if distances[best_match_index] >= threshold else known_face_names[best_match_index]
            recognized_faces.append({
                'name': name,
                'top': top,
                'right': right,
                'bottom': bottom,
                'left': left,
                'result_filename': f'static/result_{name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg',
                'folder_name': known_face_names[best_match_index] if name != "Bilinmiyor" else None
            })

        return recognized_faces

    except Exception as e:
        print(f"Hata: {e}")
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'Dosya seçilmedi'})

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Dosya seçilmedi'})

        if file:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)

            known_face_encodings, known_face_names = load_known_faces()

            unknown_image = face_recognition.load_image_file(filename)
            augmented_images = augment_image(unknown_image)

            recognized_faces_list = []

            for i, aug_img in enumerate(augmented_images):
                recognized_faces = recognize_faces(aug_img, known_face_encodings, known_face_names)

                for face in recognized_faces:
                    if face['name'] == "Bilinmiyor":
                        cv2.rectangle(aug_img, (face['left'], face['top']), (face['right'], face['bottom']), (255, 0, 0), 2)
                        cv2.putText(aug_img, face['name'], (face['left'], face['top'] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    else:
                        folder_name = face['folder_name']
                        cv2.rectangle(aug_img, (face['left'], face['top']), (face['right'], face['bottom']), (0, 255, 0), 2)
                        cv2.putText(aug_img, folder_name, (face['left'], face['top'] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        save_individual_face(aug_img, folder_name)

                if any(face['name'] != "Bilinmiyor" for face in recognized_faces):
                    result_filename = f'static/result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
                    cv2.imwrite(result_filename, cv2.cvtColor(aug_img, cv2.COLOR_BGR2RGB))
                    recognized_faces_list.extend(recognized_faces)

                    with open(KNOWN_FACES_FILE, 'wb') as face_data_file:
                        pickle.dump((known_face_encodings, known_face_names), face_data_file)

                    return jsonify({'image_path': filename, 'recognized_faces': recognized_faces_list, 'recognized_image_path': result_filename})

            return jsonify({'image_path': filename, 'recognized_faces': []})

    return render_template('basari_siralama.html')

def save_individual_face(image, folder_name):
    individual_folder_path = os.path.join('Yüzler', folder_name)
    if not os.path.exists(individual_folder_path):
        os.makedirs(individual_folder_path)

    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    individual_file_path = os.path.join(individual_folder_path, f"yuz_{folder_name}_{current_time}.jpg")
    cv2.imwrite(individual_file_path, cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

if __name__ == '__main__':
    app.run(debug=True)