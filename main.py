from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from PIL import Image
import numpy as np
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'random_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Bootstrap(app)


def allowed_file(filename):
    # '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS --> Meaning:
    # (If dot in filename == True) --> ('.' in filename)   &
    # (filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS == True)
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb


def extract_colors(np_image):
    counter = {}
    for i in np_image[0]:
        if str(i) not in counter:
            counter[str(i)] = 1
        else:
            counter[str(i)] += 1
    sorted_counter = {k: v for k, v in sorted(counter.items(), key=lambda item: item[1], reverse=True)}
    colors_list = [list(sorted_counter.keys())[:10], list(sorted_counter.values())[:10]]

    top_10_colors = []
    for n in range(len(colors_list[0])):
        x = colors_list[0][n][1:-1].split(' ')
        while '' in x:
            x.remove('')
        for i in range(len(x)):
            x[i] = int(x[i])
        top_10_colors.append([f'#{rgb_to_hex(tuple(x))}',
                              round((colors_list[1][n]) * 100 / (sum(sorted_counter.values())), 2)])
    return top_10_colors


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            # print('prova')
            # SAVE FILE
            filename = secure_filename(file.filename)
            # print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # EXTRACTING COLORS
            pil_image = Image.open(file).convert('RGB')
            # print(pil_image)
            np_image = np.array(pil_image)
            # print(f'np_image : {np_image}')

            top_colors = extract_colors(np_image=np_image)
            print(top_colors)
            flash('File uploaded successfully')
            return render_template('index.html', file=filename, colors=top_colors)
        else:
            # WRONG EXTENSION
            flash('Allowed image types are: png, jpg, jpeg, gif')
            return render_template('index.html')

    return render_template('index.html')


@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename=f'images/{filename}'), code=301)


if __name__ == '__main__':
    app.run(debug=True)