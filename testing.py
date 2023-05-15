import os
import numpy as np
from flask import Flask, render_template, request, redirect, flash
import lyricsgenius;
from gevent.pywsgi import WSGIServer
import spotipy;
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth;
import pandas as pd;
import requests
from bs4 import BeautifulSoup
from langdetect import detect;
from spotipy.exceptions import SpotifyException
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from textblob import TextBlob
import re
from waitress import serve
import time;
from flask_socketio import SocketIO, emit;
# Importing File Content_Filtering.py
import Content_Filtering as cf;
df = pd.read_csv("actdata.csv");

def nsu(ans):
    global df;
    cond_str_lang = "df['language'] == "
    cond_str_genre = "df['genres'] == "
    cond_str_artist = "df['artist_name'] == "
    total_cond = [];
    for i in ans[0]:
        x = cond_str_lang;
        i = "'" + i + "'";
        x += i
        print(x)
        total_cond.append(x)
    for i in ans[1]:
        x = cond_str_genre;
        i = "'" + i + "'";
        x += i
        print(x)
        total_cond.append(x)
    for i in ans[2]:
        x = cond_str_artist;
        i = "'" + i + "'";
        x += i
        print(x)
        total_cond.append(x);
    apper = 0
    for i in total_cond:
        apper |= (eval(i));
    return df[apper].sort_values("track_pop", ascending=False);



script_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.abspath(script_dir)
app = Flask(__name__, template_folder=template_dir, static_folder='static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def extractor(linkers):
    playlist_data = [];
    client_credentials_manager = SpotifyClientCredentials(client_id="8bf3b765c2da43c395a436cd0745db80", client_secret="7c70696eefde4544b020fc74f9096691");
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager);
    playlist_link = linkers;
    playlist_URI = playlist_link.split("/")[-1].split("?")[0];
    track_uris = [x["track"]["uri"] for x in sp.playlist_tracks(playlist_URI)["items"]];
    playlist_id = playlist_URI;
    results = sp.playlist_tracks(playlist_id);
    tracks = results['items'];
    while results['next']:
        results = sp.next(results);
        tracks.extend(results['items']);
    i = 0
    def get_artist_url(track):
        track = "https://open.spotify.com/artist/" + track['track']['artists'][0]['uri'].split(':')[-1];
        return track;
    def get_track_url(track):
        return sp.track(track)['external_urls']['spotify'];
    try:
        initial = []
        for track in tracks[:20]:
            track_uri = track['track']['uri'];
            track_id = track_uri.split(':')[-1];
            track_data = {
                'artist_name': track['track']['artists'][0]['name'],
                'track_uri': track_uri,
                'track_url': get_track_url(track_uri),
                'artist_uri': track['track']['artists'][0]['uri'],
                'artist_url': get_artist_url(track),
                'track_name': track['track']['name'],
                'album_uri':track['track']['album']['uri'],
                'duration_ms_x': track['track']['duration_ms'],
                'album_name': track['track']['album']['name'],
                'name':track['track']['name'],
                'danceability':sp.audio_features(track_uri)[0]['danceability'],
                'energy':sp.audio_features(track_uri)[0]['energy'],
                'key':sp.audio_features(track_uri)[0]['key'],
                'loudness':sp.audio_features(track_uri)[0]['loudness'],
                'mode':sp.audio_features(track_uri)[0]['mode'],
                'speechiness':sp.audio_features(track_uri)[0]['speechiness'],
                'acousticness':sp.audio_features(track_uri)[0]['acousticness'],
                'instrumentalness':sp.audio_features(track_uri)[0]['instrumentalness'],
                'liveness':sp.audio_features(track_uri)[0]['liveness'],
                'valence':sp.audio_features(track_uri)[0]['valence'],
                'tempo':sp.audio_features(track_uri)[0]['tempo'],
                'type':sp.audio_features(track_uri)[0]['type'],
                'id':sp.audio_features(track_uri)[0]['id'],
                'uri':sp.audio_features(track_uri)[0]['uri'],
                'track_href':sp.audio_features(track_uri)[0]['track_href'],
                'analysis_url':sp.audio_features(track_uri)[0]['analysis_url'],
                'duration_ms_y':sp.audio_features(track_uri)[0]['duration_ms'],
                'time_signature':sp.audio_features(track_uri)[0]['time_signature'],
                'artist_pop':sp.artist(track['track']['artists'][0]['uri'])['popularity'],
                'genres':sp.artist(track['track']['artists'][0]['uri'])['genres'],
                'track_pop':sp.track(track_uri)['popularity']
            }
            playlist_data.append(track_data)
            socketio.emit("info",track_data);
            i += 1;
            print("No of Songs Extracted = ",i);
    except SpotifyException as e:
        print("Limit Exceeded !!!");
    print("Total Number of Songs : ",len(playlist_data))
    playlist_df = pd.DataFrame(playlist_data)
    # playlist_df.to_csv("testplist.csv");
    return playlist_df;




@app.route('/')
def index():
    return render_template('search.html');
labeler = ""
@app.route('/process', methods=['POST'])
def handle_form_submission():
    if request.method == "POST":
        global labeler;
        labeler = request.form['my_textbox'];
        return redirect('/process2');
    return render_template('search.html');
@socketio.on('connect')
@app.route('/process2', methods=['POST', 'GET'])
def langsd():
    print("Hello")
    global labeler;
    lang_list = [];
    if request.method == 'POST':
        answer = request.form.getlist('vehicle1')
        lang_list.append(answer)
        text = extractor(labeler);
        text = cf.content_filtering(text, lang_list);
        text = text.to_dict(orient='records');
        return render_template('tq.html', dicter=text);
    return render_template('lang.html', langer = np.random.permutation(df["language"].unique()))


answers = []
@app.route('/set', methods=['GET', 'POST'])
def home():
    return redirect('/question1')

@app.route('/question1', methods=['GET', 'POST'])
def question1():
    print("One Done {}".format(df["language"].unique()));
    if request.method == 'POST':
        answer = request.form.getlist('vehicle1')
        answers.append(answer)
        return redirect('/question2')
    return render_template('q1.html', langer = df["language"].unique())

@app.route('/question2', methods=['GET', 'POST'])
def question2():
    print("Two Done {}".format(df["genres"].unique()));
    if request.method == 'POST':
        answer = request.form.getlist('vehicle1')
        answers.append(answer)
        return redirect('/question3')
    return render_template('q2.html')

@app.route('/question3', methods=['GET', 'POST'])
def question3():
    print("Three Done {}".format(df["artist_name"].unique()));
    if request.method == 'POST':
        answer = request.form.getlist('vehicle1')
        answers.append(answer)
        return redirect('/result')
    return render_template('q3.html')

@app.route('/result')
def result():
    print(answers);
    data_frame = nsu(answers);
    data_frame = data_frame.to_dict(orient='records');
    time.sleep(1);
    return render_template('tq.html', dicter=data_frame);

if __name__ == '__main__': 
    # app.run(debug=True)
    # server = WSGIServer(("localhost", 121), app);
    # server.serve_forever();
    socketio.run(app, debug=True)
    # serve(app, host="0.0.0.0", port=8080)
# labeler = pd.read_csv("D:/Project/python_trail/testplist.csv");
# print(type(cf(labeler)))
