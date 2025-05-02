from flask import Flask, request, jsonify
import easyocr
import re
from PIL import Image
import io
import numpy as np
import time  # Import the time module
from waitress import serve  # ✅ Optional: use this instead of Flask's dev server

app = Flask(__name__)

# Aadhaar number pattern: 12 digits, often grouped as 4-4-4
AADHAAR_REGEX = r'\b\d{4}\s\d{4}\s\d{4}\b|\b\d{12}\b'

# ✅ Initialize EasyOCR reader only once
print("Loading EasyOCR model...")
reader = easyocr.Reader(['en'])
print("EasyOCR model loaded.")

@app.route('/extract_aadhaar', methods=['POST'])
def extract_aadhaar():
    print('[*] Received request')

    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded."}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"error": "Empty file uploaded."}), 400

    try:
        start_time = time.time()  # Start timing the processing

        print('[*] Processing image...')
        image = Image.open(io.BytesIO(image_file.read()))
        np_image = np.array(image)

        image_processing_time = time.time() - start_time  # Time taken for image processing
        print(f'[*] Image processing completed in {image_processing_time:.2f} seconds')

        print('[*] Running OCR...')
        start_time = time.time()  # Start timing OCR

        result = reader.readtext(np_image)

        ocr_time = time.time() - start_time  # Time taken for OCR
        print(f'[*] OCR completed in {ocr_time:.2f} seconds')

        print('[*] Extracting text...')
        start_time = time.time()  # Start timing text extraction

        text = ' '.join([item[1] for item in result])
        aadhaar_numbers = re.findall(AADHAAR_REGEX, text)
        aadhaar_numbers = [num.replace(' ', '') for num in aadhaar_numbers]

        text_extraction_time = time.time() - start_time  # Time taken for text extraction
        print(f'[*] Text extraction completed in {text_extraction_time:.2f} seconds')

        print('[*] Aadhaar Numbers:', aadhaar_numbers)

        if not aadhaar_numbers:
            return jsonify({"message": "No Aadhaar number found."}), 404

        return jsonify({"aadhaar_numbers": aadhaar_numbers}), 200

    except Exception as e:
        print('[!] Error:', str(e))
        return jsonify({"error": str(e)}), 500

# ✅ Run with waitress (better performance than Flask dev server)
if __name__ == '__main__':
    print("Starting server on http://127.0.0.1:5000")
    serve(app, host='127.0.0.1', port=5000)
