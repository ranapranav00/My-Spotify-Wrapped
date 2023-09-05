from flask import Flask, request, url_for, session, redirect, jsonify
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from secretconfigs import CLIENT_ID, CLIENT_SECRET, SECRET_KEY
import time


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = url_for("redirectPage", _external=True), #url_for("redirectPage", _external=True), #_external=True makes it an absolute URL rather than relative (https:/...)
        scope = "user-top-read user-library-read" # what information we need from users, only user-top-read is really necessary
    )

app = Flask(__name__)
CORS(app, origins="http://localhost:3000", supports_credentials=True)
app.secret_key = SECRET_KEY # Secret key is not specific to spotify, but used in any flask app in order to encrypt/protect the 
                            # cookies. It is supposedly good practice to store this in a separate file
app.config['SESSION_COOKIE_NAME'] = 'Myspotifywrapped Cookie'
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/redirectPage")
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect(url_for("getTracks", _external=True))


#def get_artist_data(mode):
#    return [artist['id'] for artist in mode['album']]

#def get_track_data(mode):
#    return [song['id'] for song in mode['items']]

def validate_token():
    token_info = session.get("token_info", None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    if ((token_info['expires_at'] - now) < 60):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

@app.route("/getTracks")
def getTracks():
    try:
        token_info = validate_token()
    except:
        print("You must log in!")
        return redirect("/")
    

    spotify_instance = spotipy.Spotify(
        auth = token_info['access_token'],
    )
    

    top10artists = spotify_instance.current_user_top_artists(
        limit=10,
        offset=0,
        time_range="long_term"
    )
    

    top3tracks = spotify_instance.current_user_top_tracks(
        limit=10,
        offset=0,
        time_range="long_term"
    )

    top10tracks = spotify_instance.current_user_top_tracks(
        limit=10,
        offset=0,
        time_range="long_term"
    )
    
    response = jsonify(spotify_instance.current_user_top_artists(
        limit=2,
        offset=0,
        time_range="long_term"
    ))
    response.headers.add('Access-Control-Allow-Origin', 'http://127.0.0.1:5000/getTracks')
    return response