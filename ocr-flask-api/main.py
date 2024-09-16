from flask import Flask, request, jsonify, send_file, url_for
from flask_cors import CORS  # Importar CORS
import os
import keras_ocr
import matplotlib.pyplot as plt
import uuid
import gc
import shutil
import threading
import easyocr

# Crear el pipeline de Keras-OCR y el lector de EasyOCR
pipeline = keras_ocr.pipeline.Pipeline()
easyocr_reader = easyocr.Reader(['en'])

# Inicializar la aplicación Flask
app = Flask(__name__)
CORS(app)  # Habilitar CORS aquí

# Guardar las imágenes temporalmente en una carpeta
UPLOAD_FOLDER = 'processed_images'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Ruta para subir y procesar la imagen
@app.route('/procesar-imagen', methods=['POST'])
def procesar_imagen():
    # Verificar que se ha enviado una imagen
    if 'image' not in request.files or 'ocr_method' not in request.form:
        return jsonify({"error": "No se ha proporcionado una imagen o el método de OCR"}), 400

    # Leer la imagen enviada por el usuario usando Keras-OCR tools
    image_file = request.files['image']
    ocr_method = request.form['ocr_method']
    image = keras_ocr.tools.read(image_file.stream)

    extracted_text = ""
    prediction_groups = []

    # Procesar la imagen según el método seleccionado
    if ocr_method == 'keras':
        prediction_groups = pipeline.recognize([image])[0]
        extracted_text = " ".join([prediction[0] for prediction in prediction_groups])
    elif ocr_method == 'easyocr':
        results_easyocr = easyocr_reader.readtext(image)
        extracted_text = " ".join([result[1] for result in results_easyocr])
        prediction_groups = [(result[0], result[1]) for result in results_easyocr]

    # Crear una imagen en blanco para superponer las anotaciones
    fig, ax = plt.subplots()
    ax.imshow(image)

    if ocr_method == 'keras':
        keras_ocr.tools.drawAnnotations(image=image, predictions=prediction_groups, ax=ax)
    elif ocr_method == 'easyocr':
        for (bbox, text) in prediction_groups:
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))
            ax.add_patch(plt.Rectangle(top_left, bottom_right[0] - top_left[0], bottom_right[1] - top_left[1],
                                       edgecolor='green', facecolor='none', linewidth=2))
            ax.text(top_left[0], top_left[1] - 10, f'{text}', color='green', fontsize=12, weight='bold')

    # Generar un nombre único para la imagen procesada
    unique_filename = f"{uuid.uuid4()}.jpg"
    output_image_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    # Guardar la imagen procesada temporalmente usando matplotlib
    plt.axis('off')
    plt.savefig(output_image_path, bbox_inches='tight', pad_inches=0, format='jpg')
    plt.close(fig)  # Cerrar la figura para liberar memoria
    gc.collect()  # Liberar memoria

    # Responder con el texto extraído y una URL para descargar la imagen
    return jsonify({
        "text": extracted_text,
        "image_url": url_for('download_image', filename=unique_filename, _external=True)
    })

# Ruta para descargar la imagen procesada
@app.route('/download/<filename>', methods=['GET'])
def download_image(filename):
    # Construir la ruta del archivo
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Verificar si el archivo existe
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    # Enviar el archivo
    response = send_file(file_path, mimetype='image/jpeg')

    # Eliminar el archivo después de un breve retraso
    def remove_file():
        import time
        time.sleep(1)  # Esperar un segundo antes de eliminar el archivo
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")

    threading.Thread(target=remove_file).start()

    return response

# Iniciar la aplicación
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
