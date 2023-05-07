import os
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
# Importing File Content_Filtering.py
import Content_Filtering as cf;
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
        for track in tracks[:50]:
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
            i += 1;
            print("No of Songs Extracted = ",i);
    except SpotifyException as e:
        print("Limit Exceeded !!!");
    print("Total Number of Songs : ",len(playlist_data))
    playlist_df = pd.DataFrame(playlist_data)
    # playlist_df.to_csv("testplist.csv");
    return playlist_df;
text = extractor("https://open.spotify.com/playlist/6hgMqj2cRyGKbC4tNLq3Rb?si=5dd919d9501e486f");
text = cf.content_filtering(text);
text.to_csv("del.csv")