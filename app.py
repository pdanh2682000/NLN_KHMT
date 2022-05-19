from flask import Flask, render_template, Response, request, jsonify
from mtcnn import MTCNN
import numpy as np
from PIL import Image
import random


from face_search import search_face

app = Flask(__name__)

# Detect face, search face and display results
detector = MTCNN()


def convert_from_image_to_cv2(img: Image) -> np.ndarray:
    # return cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)
    return np.asarray(img)

@app.route('/', methods=['GET'])
def welcome():
    return render_template('home.html')

@app.route('/form_find', methods=['GET'])
def form_find():
    return render_template('form_find.html')

@app.route('/film_find', methods=['GET'])
def film_find():
    return render_template('film_find.html')

@app.route("/handle_form_find", methods=["POST"])
def handle_form_file_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({'message': 'No file found'}), 400 # status code fail from client
        try:
            file = request.files['image']
            file.save('./static/'+file.filename)
            # Read the image via file.stream
            im = Image.open(file.stream)
            image = convert_from_image_to_cv2(im)
            faces = detector.detect_faces(image)  # xem co bao nhieu guong mat trong hinh
            print("Results:")
            names = []
            similaritys = []
            counts = 0
            for face in faces:
                if face['confidence'] > 0.8:
                    counts = counts + 1
                    bounding_box = face['box']

                    # cut face from image
                    crop_img = im.crop((bounding_box[0], bounding_box[1],
                                        bounding_box[0] + bounding_box[2], bounding_box[1] + bounding_box[3]))

                    name, similarity = search_face(crop_img)
                    names.append(name)
                    similaritys.append(similarity)

            print("---------------")

            if counts != 0:
                return render_template('form_find.html', name=names, picture=file.filename)
            else:
                return jsonify({'message': 'picture not detected face'}), 500 # status code fail from client
        except:
            return jsonify({'message': 'failure'}), 500 # status code fail from server
    else:
        return jsonify({'message': 'HTTP method request incorrect'}), 400  # status code fail from client


@app.route("/handle_film_find", methods=["POST"])
def handle_film_file_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({'message': 'No file found'}), 400 # status code fail from client
        try:
            file = request.files['image']
            # file.save('./static/'+file.filename)
            # Read the image via file.stream
            im = Image.open(file.stream)
            image = convert_from_image_to_cv2(im)
            faces = detector.detect_faces(image)  # xem co bao nhieu guong mat trong hinh
            print("Results:")
            names = []
            similaritys = []
            counts = 0
            for face in faces:
                if face['confidence'] > 0.8:
                    counts = counts + 1
                    bounding_box = face['box']

                    # cut face from image
                    crop_img = im.crop((bounding_box[0], bounding_box[1],
                                        bounding_box[0] + bounding_box[2], bounding_box[1] + bounding_box[3]))

                    name, similarity = search_face(crop_img)
                    names.append(name)
                    similaritys.append(similarity)

            print("---------------")

            if counts != 0:
                return render_template('result_film_find.html', name=names[0], picture=file.filename)
            else:
                return jsonify({'message': 'picture not detected face'}), 500 # status code fail from client
        except:
            return jsonify({'message': 'failure'}), 500 # status code fail from server
    else:
        return jsonify({'message': 'HTTP method request incorrect'}), 400  # status code fail from client


# API for External Application
@app.route("/api/v1", methods=["POST"])
# @crossdomain(origin='*',headers=['access-control-allow-origin','Content-Type'])
def process_image():
    Response.headers.add('Access-Control-Allow-Origin', '*')
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({'message': 'No file found'}), 400 # status code fail from client
        try:
            file = request.files['image']
            # Read the image via file.stream
            im = Image.open(file.stream)
            image = convert_from_image_to_cv2(im)
            faces = detector.detect_faces(image)  # xem co bao nhieu guong mat trong hinh
            print("Results:")
            names = []
            similaritys = []
            counts = 0
            for face in faces:
                if face['confidence'] > 0.8:
                    counts = counts + 1
                    bounding_box = face['box']

                    # cut face from image
                    crop_img = im.crop((bounding_box[0], bounding_box[1],
                                        bounding_box[0] + bounding_box[2], bounding_box[1] + bounding_box[3]))

                    name, similarity = search_face(crop_img)
                    names.append(name)
                    similaritys.append(similarity)

            print("---------------")

            if counts != 0:
                return jsonify({'message': 'success', 'size': [im.width, im.height], 'count': counts,
                                'name': names, 'similarity': str(similaritys)})
            else:
                return jsonify({'message': 'picture not detected face'}), 500 # status code fail from client
        except:
            return jsonify({'message': 'failure'}), 500 # status code fail from server
    else:
        return jsonify({'message': 'HTTP method request incorrect'}), 400  # status code fail from client


if __name__ == '__main__':
    app.run(debug=True)
