# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import pawprint

app = dash.Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
fig = pawprint.draw_bearable_fig(pawprint.BearableData('../bearable-export-19-12-2021.csv'))

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
html.Div(
    dcc.Graph(
        id='bearable-graph',
        figure=fig
    )
)])

@app.callback(Output('bearable-graph', 'contents'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

if __name__ == '__main__':
    app.run_server(debug=True)