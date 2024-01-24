import face_recognition
import os
import pickle

def process_and_save_face_encodings(folder_path='Yüzler', output_file='know_facess.dat'):
    """
    Belirtilen klasördeki her yüz resmini işler ve yüz özelliklerini (encodings) ile 
    ilgili kişilerin isimlerini bir dosyada saklar.

    Args:
    folder_path: Yüz resimlerinin saklandığı klasörün yolu. Varsayılan olarak 'bilinen_yuzler'.
    output_file: Yüz özelliklerinin ve isimlerinin kaydedileceği dosyanın adı. Varsayılan olarak 'known_faces.dat'.
    
    Bu fonksiyon, her bir yüz resmi için face_recognition kütüphanesini kullanarak yüz özelliklerini çıkarır.
    Çıkarılan her yüz özelliği ve ilgili kişinin ismi, belirtilen dosyada pickle formatında saklanır.

    Örnek Kullanım:
    process_and_save_face_encodings()
    """

    known_face_encodings = []
    known_face_names = []

    for person_name in os.listdir(folder_path):
        person_folder = os.path.join(folder_path, person_name)
        if os.path.isdir(person_folder):
            for filename in os.listdir(person_folder):
                if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg'):
                    image_path = os.path.join(person_folder, filename)
                    image = face_recognition.load_image_file(image_path)
                    face_encodings = face_recognition.face_encodings(image)
                    if face_encodings:
                        known_face_encodings.append(face_encodings[0])
                        known_face_names.append(person_name)

    # Yüz özelliklerini ve isimlerini bir dosyaya kaydet
    with open(output_file, 'wb') as face_data_file:
        pickle.dump((known_face_encodings, known_face_names), face_data_file)

process_and_save_face_encodings()