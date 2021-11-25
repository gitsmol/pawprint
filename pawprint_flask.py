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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def load():

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            errormessage='No file sent.'
            flash('No file part')
            return render_template('error.html', errormessage=errormessage)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            errormessage = 'No file selected.'
            return render_template('error.html', errormessage=errormessage)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                df = pd.read_csv(file)
                fig = pawprint.graph(df)
            except Exception as e:
                errormessage = e
                return render_template('error.html', filename=filename, errormessage=errormessage)

            graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            header="Bearable csv"
            description = """
            Returns import of Bearable csv.
            """     
            return render_template('graph.html', filename=filename, graph_json=graph_json)

    return render_template('index.html')

@app.route('/about')
def about():    
    return render_template('about.html')

if __name__ == '__main__':
    app.run(host='192.168.1.101', debug=True)
