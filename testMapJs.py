import dash
from dash import Dash, dcc, html, Input, Output, callback, ClientsideFunction
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

app = dash.Dash(__name__)

# app.layout = html.Div([
#     dcc.Location(id='url', refresh=False),
#     html.Iframe(id='map-iframe', srcDoc=open('mapa.html', 'r').read(), width='100%', height='600px'),
#     dcc.Input(id='input-parametro', type='text', value=''),
#     html.Button('Invocar función JS', id='btn-invocar'),
#     
# ], id = 'MainLabel', )

app.layout = html.Div([
    html.Button("Invoke JavaScript Function", id="invoke-button"),
    html.Script(src='./externalFunc.js')
])

@app.callback(
    Output("output-div", "children"),
    Input("invoke-button", "n_clicks")
)
def invoke_js_function(n_clicks):
    if n_clicks is not None:
        return html.Script("myExternalFunction('Hello from Dash!');")
    return ""

if __name__ == '__main__':
    app.run_server(debug=True)