# OCR Image Processing API with Flask, Keras-OCR, and EasyOCR

This repository contains a Flask-based API for Optical Character Recognition (OCR) using `keras-ocr` and `easyocr` to extract text from images. The API allows users to upload an image and choose between two OCR methods for text extraction: Keras-OCR and EasyOCR. The processed image is then returned along with the extracted text.

## Features

- Upload an image and process it using either Keras-OCR or EasyOCR.
- Return the extracted text from the image.
- Superimpose OCR annotations on the image and return the processed image.
- Supports CORS (Cross-Origin Resource Sharing) for easy integration with other web services.
- Deletes processed images after being served to the client.

## Prerequisites

Before running this project, ensure you have the following dependencies installed:

- Python 3.19
- `Flask`
- `Flask-CORS`
- `keras-ocr`
- `easyocr`
- `matplotlib`
- `threading`

You can install the dependencies using `pip`:

```bash
pip install Flask Flask-CORS keras-ocr easyocr matplotlib
```

##Running the Application
Clone this repository:

```
git clone https://github.com/fenixdorad0/tensorocr
cd ocr-flask-api
pip install -r requirements.txt
python app.py
```
The API will be available at http://localhost:5000.

##API Endpoints

/procesar-imagen

Form parameters:

image (form-data): The image file to be processed.
ocr_method (form-data): The OCR method to use. It can be:
keras: To use the Keras-OCR OCR model.
easyocr: To use the EasyOCR OCR model.

Example request:
When you send the POST request to /procesar-imagen, it must include the image and the ocr_method field. This is how it would look in curl:
```
curl -X POST http://localhost:5000/procesar-imagen \
  -F “image=@path_to_your_image.jpg” \
  -F “ocr_method=keras” # or “ocr_method=easyocr”
```
