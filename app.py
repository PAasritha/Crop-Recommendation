import os
from flask import Flask, redirect, url_for, render_template, request, session, flash
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

# Data loading and cleaning
df = pd.read_csv('Crop_recommendation.csv')

# Features and targets
features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
target = 'label'

feature_options = [{'label': feature, 'value': feature} for feature in features]
crop_options = [{'label': crop, 'value': crop} for crop in df['label'].unique()]

# Initialize Flask
server = Flask(__name__)

# Generate a random secret key
server.secret_key = os.urandom(24)

# Dummy user database (replace with a real database in a production environment)
users = {'aasritha': '1234'}

# Flask routes for login and registration
@server.route('/')
def home():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@server.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username] == password:
        session['logged_in'] = True
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials')
        return redirect(url_for('home'))

@server.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('home'))

@server.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users:
            users[username] = password
            flash('Registration successful. Please log in.')
            return redirect(url_for('home'))
        else:
            flash('Username already exists')
            return redirect(url_for('register'))
    return render_template('register.html')

# Initialize Dash
app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')

# Ensure users are redirected to login if not authenticated
@app.server.before_request
def before_request():
    if request.path.startswith('/dashboard') and 'logged_in' not in session and request.endpoint != 'login' and request.endpoint != 'static':
        return redirect(url_for('home'))

@app.server.route('/dashboard/')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('home'))
    return app.index()

# Dash layout
app.layout = html.Div([
    html.Div([
        html.Hr(),
        html.H1('Crop Recommendation Dataset'),
        html.P('The data used for this app is from the following link:'),
        html.A('Crop Recommendation Dataset', href='https://www.kaggle.com/atharvaingle/crop-recommendation-dataset')
    ]),
    html.Div([
        html.Hr(),
        html.H2('Crop wise statistics'),
        html.Div('Select the crop type:'),
        dcc.Dropdown(id='crop-picker', options=crop_options, value='rice'),
        html.Div([
            html.P('N (Nitrogen)'),
            html.P(id='N (Nitrogen) mean'),
            html.P(id='N (Nitrogen) range')
        ], style={'display': 'inline-block', 'width': '14%'}),
        html.Div([
            html.P('P (Phosphorus)'),
            html.P(id='P (Phosphorus) mean'),
            html.P(id='P (Phosphorus) range')
        ], style={'display': 'inline-block', 'width': '14%'}),
        html.Div([
            html.P('K (Potassium)'),
            html.P(id='K (Potassium) mean'),
            html.P(id='K (Potassium) range')
        ], style={'display': 'inline-block', 'width': '14%'}),
        html.Div([
            html.P('Temperature'),
            html.P(id='Temperature mean'),
            html.P(id='Temperature range')
        ], style={'display': 'inline-block', 'width': '14%'}),
        html.Div([
            html.P('Humidity'),
            html.P(id='Humidity mean'),
            html.P(id='Humidity range')
        ], style={'display': 'inline-block', 'width': '14%'}),
        html.Div([
            html.P('pH'),
            html.P(id='pH mean'),
            html.P(id='pH range')
        ], style={'display': 'inline-block', 'width': '15%'}),
        html.Div([
            html.P('Rainfall'),
            html.P(id='Rainfall mean'),
            html.P(id='Rainfall range')
        ], style={'display': 'inline-block', 'width': '15%'})
    ]),
    html.Div([
        html.Hr(),
        html.H2('Violin plots'),
        dcc.Dropdown(id='feature-picker', options=feature_options, value='N'),
        dcc.Graph(id='violin_plot')
    ]),
    html.Div([
        dcc.Location(id='url', refresh=True),
        html.Button('Sign Out', id='signout-button', n_clicks=0)
    ])
])

# Callback for sign out button and redirect
@app.callback(Output('url', 'pathname'), [Input('signout-button', 'n_clicks')])
def signout_and_redirect(n_clicks):
    if n_clicks > 0:
        session.pop('logged_in', None)
        session.pop('username', None)
        return '/'
    return dash.no_update

# Dash callbacks for updating the statistics
@app.callback(
    [
        Output('N (Nitrogen) mean', 'children'),
        Output('N (Nitrogen) range', 'children'),
        Output('P (Phosphorus) mean', 'children'),
        Output('P (Phosphorus) range', 'children'),
        Output('K (Potassium) mean', 'children'),
        Output('K (Potassium) range', 'children'),
        Output('Temperature mean', 'children'),
        Output('Temperature range', 'children'),
        Output('Humidity mean', 'children'),
        Output('Humidity range', 'children'),
        Output('pH mean', 'children'),
        Output('pH range', 'children'),
        Output('Rainfall mean', 'children'),
        Output('Rainfall range', 'children')
    ],
    [Input('crop-picker', 'value')]
)
def update_statistics(selected_crop):
    crop_df = df[df['label'] == selected_crop]
    N_mean = 'Mean: ' + str(round(crop_df['N'].mean(), 2))
    N_range = 'Range: ' + str(round(crop_df['N'].min(), 2)) + ' - ' + str(round(crop_df['N'].max(), 2))
    P_mean = 'Mean: ' + str(round(crop_df['P'].mean(), 2))
    P_range = 'Range: ' + str(round(crop_df['P'].min(), 2)) + ' - ' + str(round(crop_df['P'].max(), 2))
    K_mean = 'Mean: ' + str(round(crop_df['K'].mean(), 2))
    K_range = 'Range: ' + str(round(crop_df['K'].min(), 2)) + ' - ' + str(round(crop_df['K'].max(), 2))
    temperature_mean = 'Mean: ' + str(round(crop_df['temperature'].mean(), 2))
    temperature_range = 'Range: ' + str(round(crop_df['temperature'].min(), 2)) + ' - ' + str(round(crop_df['temperature'].max(), 2))
    humidity_mean = 'Mean: ' + str(round(crop_df['humidity'].mean(), 2))
    humidity_range = 'Range: ' + str(round(crop_df['humidity'].min(), 2)) + ' - ' + str(round(crop_df['humidity'].max(), 2))
    ph_mean = 'Mean: ' + str(round(crop_df['ph'].mean(), 2))
    ph_range = 'Range: ' + str(round(crop_df['ph'].min(), 2)) + ' - ' + str(round(crop_df['ph'].max(), 2))
    rainfall_mean = 'Mean: ' + str(round(crop_df['rainfall'].mean(), 2))
    rainfall_range = 'Range: ' + str(round(crop_df['rainfall'].min(), 2)) + ' - ' + str(round(crop_df['rainfall'].max(), 2))
    
    return [N_mean, N_range, P_mean, P_range, K_mean, K_range, temperature_mean, temperature_range, humidity_mean, humidity_range, ph_mean, ph_range, rainfall_mean, rainfall_range]

@app.callback(Output('violin_plot', 'figure'), [Input('feature-picker', 'value')])
def update_violin_plot(selected_feature):
    figure = {
        'data': [
            go.Violin(
                y=df[df['label'] == crop][selected_feature],
                name=crop,
                box_visible=True,
                meanline_visible=True
            ) for crop in df['label'].unique()
        ],
        'layout': go.Layout(
            title='Violin plot of ' + selected_feature,
            yaxis={'title': selected_feature}
        )
    }
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)

