from flask import Flask, request, jsonify
import easyocr
import re
from PIL import Image
import io

app = Flask(__name__)

# Aadhaar number pattern: 12 digits, often grouped as 4-4-4
AADHAAR_REGEX = r'\b\d{4}\s\d{4}\s\d{4}\b|\b\d{12}\b'

# Initialize easyocr reader
reader = easyocr.Reader(['en'])

@app.route('/extract_aadhaar', methods=['POST'])
def extract_aadhaar():
    print('1')
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded."}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"error": "Empty file uploaded."}), 400

    try:
        # Convert the uploaded image to a PIL Image object
        image = Image.open(io.BytesIO(image_file.read()))

        # Use easyocr to extract text from the image
        result = reader.readtext(image)

        # Extract text (only the string parts of the result)
        text = ' '.join([item[1] for item in result])

        # Find Aadhaar numbers using the regex
        aadhaar_numbers = re.findall(AADHAAR_REGEX, text)
        aadhaar_numbers = [num.replace(' ', '') for num in aadhaar_numbers]  # Normalize

        if not aadhaar_numbers:
            return jsonify({"message": "No Aadhaar number found."}), 404

        return jsonify({"aadhaar_numbers": aadhaar_numbers}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)