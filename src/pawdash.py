import logging
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import base64
import io
import pawprint

logging.basicConfig(filename='pawprint.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s')

app = dash.Dash(__name__)
# app = dash.Dash(__name__, requests_pathname_prefix='/pawprint/')
server = app.server
logging.debug('Dash app initialized.')

app.layout = html.Div(className='wrapper', children=[
    html.Div(className='nav', children=[
        html.Div(className='block label', children=[
            html.H3('Pawprint'),
            html.Div(children=[
                html.P('''Pawprint turns Bearable data into large graphs. 
                Print or save as pdf to share your results with other people. 
                Pawprint only keeps your data while you look at it. If you leave this page, it is gone.'''),
                html.A(href='https:www.github.com/gitsmol/pawprint', children='Check out the readme to learn more.')])
        ]),
        html.Div(className='block config', children=[
            dcc.Upload(id='upload-data', className='button item', multiple=False, children=[
                html.Div(['File goes here...']),
            ]),
            html.P(className='item', children=['More features, colors and ideas are on the way. Let me know what you think on the Bearable subreddit!'])
        ]),
        html.Div(className='block config', children=[

            html.Div(className='item', children=[
                html.Label('LOWESS smoothing'),
                dcc.Slider(
                    id='graph-lowess-fraction',
                    min=0, max=0.5, value=0.1, step=0.01,
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
            ]),
            html.Div(className='item', children=[
                html.Label('Histogram period'),
                dcc.Slider(
                    id='graph-histogram-period',
                    min = 0, max = 6,
                    value=4, step=None, 
                    marks={
                        1 : '1W',
                        2 : '2W',
                        3 : '3W',
                        4 : '1M',
                        5 : '1M',
                        6 : '3M'
                    },
                    # tooltip={"placement": "bottom", "always_visible": False}
                )
            ]),
        ]),
    ]),
    html.Div(className='graph-content', children=[
        html.Div(id='output-data-upload'),
    ])
])

def get_histogram_period(value):
    return {
        1 : '1W',
        2 : '2W',
        3 : '3W',
        4 : '1M',
        5 : '2M',
        6 : '3M'
    }.get(value)

@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              Input('graph-lowess-fraction', 'value'),
              Input('graph-histogram-period', 'value')

            #   State('upload-data', 'filename'),
            #   State('upload-data', 'last_modified')
            )
def update_output(contents, lowess_fraction, histogram_period):
    logging.debug('Running update_output()')
    if contents:
        try:
            content_type, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)
            decoded = io.StringIO(decoded.decode("utf-8"))
            data = pawprint.BearableData(decoded)
            data.graph_configuration['lowess_fraction'] = lowess_fraction
            data.graph_configuration['histogram_period'] = get_histogram_period(histogram_period)
            data.build_longform()
            data.draw_bearable_fig()

        except Exception as e:
            logging.error('!!! Caught exception: %s', e)
            logging.exception('!!! Caught exception: %s', e)

            return html.P('Unable to process your file.')

        if decoded is not None:
            return html.Div(children=[
                dcc.Graph(
                    figure = data.FIG_measurements
                ),
                html.Div(children='''
            Double click the factors in the legend to disable all. Then enable the ones you want to examine. (I'm open to better ideas to manage a huge number of factors.)
        '''),
                dcc.Graph(
                    figure = data.FIG_factors
                )
            ])

if __name__ == '__main__':
    app.run_server(debug=True)