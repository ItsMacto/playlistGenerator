from flask import Flask, request, redirect, render_template, session, url_for
from dotenv import load_dotenv
import os
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = 'http://localhost:3000/callback'

seed = {'target_energy': 1}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/test')
def test():
    return 'Test route is working'


@app.route('/login')
def login():
    scope = 'user-read-private user-read-email'
    auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={CLIENT_ID}&scope={scope}&redirect_uri={REDIRECT_URI}"
    print(auth_url)
    
    return redirect(auth_url)


@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = 'https://accounts.spotify.com/api/token'
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(token_url, data=token_data)
    data = response.json()
    session['access_token'] = data['access_token']
    return redirect(url_for('home'))


@app.route('/recommendations', methods=['POST'])
def recommendations():
    mood = request.form['mood']
    access_token = session.get('access_token')
    if not access_token:
        return redirect('/login')


    energy =  float(mood) / 10
    
    tracks = fetch_spotify_recommendations(energy, access_token)
    
    # Render a template to display these tracks or handle it as you see fit
    return render_template('recommendations.html', tracks=tracks)

    
def fetch_spotify_recommendations(energy, access_token):
    url = 'https://api.spotify.com/v1/recommendations'
    params = {
        'seed_genres': 'country',  
        # 'valence': valence,
        'target_energy': energy
    }
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    print(params)
    response = requests.get(url, headers=headers, params=params)
    print(response)
    return response.json()  



if __name__ == '__main__':
    app.run(debug=True, port=3000)
