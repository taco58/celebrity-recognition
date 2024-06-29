from numpy import expand_dims
from PIL import Image
from numpy import asarray
from mtcnn.mtcnn import MTCNN
from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
from keras_vggface.utils import decode_predictions
from flask import Flask, request, jsonify, render_template
import base64
import json
import numpy
from io import BytesIO
from PIL import Image
import os
from bing_image_urls import bing_image_urls

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/show_results', methods=['GET'])
def show_results():
    results_json = request.args.get('result')
    result = json.loads(results_json)
    temp = [[result['results'][0]['label'], result['results'][0]['confidence'], result['images'][0]],
            [result['results'][1]['label'], result['results'][1]['confidence'], result['images'][1]],
            [result['results'][2]['label'], result['results'][2]['confidence'], result['images'][2]],
            [result['results'][3]['label'], result['results'][3]['confidence'], result['images'][3]],
            [result['results'][4]['label'], result['results'][4]['confidence'], result['images'][4]]]
    
    temp2 = []
    for t in temp:
        if len(t[0]) < 25:
            temp2.append(t)
    return render_template('result.html', results=temp2)

@app.route('/recognition', methods=['POST'])
def recognition():
    img_data_base64 = request.form.get('imageDataUrl')
    img_data = base64.b64decode(img_data_base64.split(',')[1])
    img = BytesIO(img_data)

    def extract_face(image, required_size=(224, 224)):
        try:
            pixels = numpy.array((Image.open(image)).convert('RGB'))
            detector = MTCNN()
            results = detector.detect_faces(pixels)
            if not results:
                return None 
            x1, y1, width, height = results[0]['box']
            x2, y2 = x1 + width, y1 + height
            face = pixels[y1:y2, x1:x2]
            image = Image.fromarray(face)
            image = image.resize(required_size)
            face_array = asarray(image)
            return face_array
        except Exception as e:
            return None 

    pixels = extract_face(img)
    if pixels is None:
        return jsonify({'error': 'No face detected'})
    pixels = pixels.astype('float32')
    samples = expand_dims(pixels, axis=0)
    samples = preprocess_input(samples, version=2)
    model = VGGFace(model='resnet50')
    yhat = model.predict(samples)
    results = decode_predictions(yhat)
    
    response = []
    for result in results[0]:
        try:
            label = result[0].decode('utf-8').strip("b' ").replace('%20', ' ')
        except:
            label = result[0]
        confidence = round(float(result[1]) * 100, 1)
        response.append({'label': label, 'confidence': confidence})
    
    images = []
    for result in response:
        result['label'] = result['label'].replace('_', ' ')
        image_urls = bing_image_urls(result['label'], limit=1)
        if not image_urls:
            return jsonify({'error': 'No image found'})
        images.append(image_urls[0])
        
    return jsonify({'results': response, 'images': images})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

    # celebrity recognition