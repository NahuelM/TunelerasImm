import dash
from dash import Dash, dcc, html, Input, Output, callback, ClientsideFunction
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

app = dash.Dash(__name__)
# mapJs = html.Iframe(id = 'map-iframe', srcDoc=open('./mapa.html', 'r').read(), width='100%', height='500px')

# button = html.Button('Generar gráfico', id='button', n_clicks = 0, className='Button')

# div = html.Div(html.H4(id='test', className="title", style={"text-align": "center"}))


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Iframe(id='map-iframe', srcDoc=open('mapa.html', 'r').read(), width='100%', height='600px'),
    dcc.Input(id='input-parametro', type='text', value=''),
    html.Button('Invocar función JS', id='btn-invocar')
], id = 'MainLabel', )

# @app.callback(
#     Output('output-serverside', 'children'),
#     [Input('input', 'value')])

# def update_output(value):
#     return 'Server says "{}"'.format(value)
def invocarFunJs(parametro):
     script = f"document.getElementById('map-iframe').contentWindow.invocarDesdePython('{parametro}')"

@app.callback(
    Output('map-iframe', 'srcDoc'),
    Input('btn-invocar', 'n_clicks'),
    Input('input-parametro', 'value')
)
def callback_invocar_funcion_js(n_clicks, parametro):
    if n_clicks is None:
        return dash.no_update

    # Invocar la función JavaScript pasando el parámetro
    script = invocarFunJs(parametro)
    
    return f"""
    <html>
        <body>
            <script>
                {script};
            </script>
        </body>
    </html>
    """

# app.clientside_callback(
    
# #     ClientsideFunction(
# #         namespace='clientside',
# #         function_name='display'
# #     ),
#     """
#     function (value) {
#         if (value && value.indexOf('--') === 0) {
#             throw window.dash_clientside.PreventUpdate;
#         }

#         if (value && value.indexOf('__') === 0) {
#             return window.dash_clientside.no_update;
#         }

#         return 'Client says "' + value + '"';
#     }
#     """,
#     Output('output-clientside', 'children'),
#     [Input('input', 'value')]
# )

if __name__ == '__main__':
    app.run_server(debug=True)