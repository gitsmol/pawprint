from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
import datetime
import pawprint

UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/bearchart', methods=['GET', 'POST'])
def bearchart():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            df = pd.read_csv(filename)
            fig = bearable_graph(df)
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            header="Bearable csv"
            description = """
            Returns import of Bearable csv.
            """     
            return render_template('pawprint_graph.html', graphJSON=graphJSON, header=header,description=description, filename=filename)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    app.run(host='192.168.1.101')