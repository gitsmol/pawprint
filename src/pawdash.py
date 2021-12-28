import dash
# import flask
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import base64
import io
# import plotly.express as px
# import plotly.graph_objects as go
# import pandas as pd
import pawprint

app = dash.Dash(__name__, requests_pathname_prefix='/pawprint/')
server = app.server

app.layout = html.Div(children=[
    html.H1(children='Pawprint'),
    html.Div(children='''
        Pawprint turns Bearable data into graphs you can examine up close.
    '''),
    html.Div(dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Don't allow multiple files to be uploaded
            multiple=False
        )),
    html.Div(id='output-data-upload')
    ])

@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents')
            #   State('upload-data', 'filename'),
            #   State('upload-data', 'last_modified')
            )
def update_output(contents):
    try:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        decoded = io.StringIO(decoded.decode("utf-8"))
        data = pawprint.BearableData(decoded)
        fig_measurements, fig_factors = pawprint.draw_bearable_fig(data)

    except Exception as e:
        print(f'Exception: {e}')
        return html.Div(['Unable to process your file.'])

    if decoded is not None:
        return html.Div(children=[
            dcc.Graph(
                figure = fig_measurements
            ),
            dcc.Graph(
                figure = fig_factors
            )
        ])

if __name__ == '__main__':
    app.run_server(debug=True)