from flask import Blueprint, jsonify, request, redirect, url_for

import base64
import requests
from datetime import datetime, timedelta

import warnings
warnings.filterwarnings("ignore")


import pandas as pd
from nltk.stem.porter import PorterStemmer
from nltk import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

api = Blueprint("api", __name__)

class MusicRecommend:
    def _init_(self):
        self.data = pd.read_csv("popular_artist.csv")
        self.df = self.data.iloc[:19000,:]
        
        self.df["text"] = self.df["text"].str.lower().replace(r"^\w\s"," ").replace(r'\n',' ',regex=True)
        self.df['text'] = self.df['text'].apply(lambda x: self.stem_text(x))
        
        self.tf_idf = TfidfVectorizer(analyzer="word", stop_words="english")
        self.vector_matrix = self.tf_idf.fit_transform(self.df['text'])
        self.similarity_matrix = cosine_similarity(self.vector_matrix)
        
        ########################################################################
    
    def stem_text(self, txt):
        token_list = word_tokenize(txt)
        vec = [PorterStemmer().stem(token) for token in token_list]
        return " ".join(vec)
    
    def recommend(self, user_song):
        recommended_songs = []
        song_index = self.df[self.df['song'] == user_song].index[0]
        sorted_similar_values = sorted(list(enumerate(self.similarity_matrix[song_index])), reverse=True, key= lambda x: x[1])
        for song_id in sorted_similar_values[1:6]:
            song_index = song_id[0]
            song = self.df.iloc[song_index,:]['song']
            artist = self.df.iloc[song_index,:]['artist']
            song_details = {"song_name": song, "artist": artist}
            recommended_songs.append(song_details)
        return recommended_songs

class Spotify:
    def __init__(self):
        self.CLIENT_ID          = ""
        self.CLIENT_SECRET      = ""
        
        self.API_ENDPOINT       = "https://api.spotify.com/v1/"
        self.AUTH_ENDPOINT      = "https://accounts.spotify.com/authorize"
        self.GET_TOKEN_ENDPOINT = "https://accounts.spotify.com/api/token"
        self.REDIRECT_URI       = "http://127.0.0.1:5000/home"
        
        ####################################################################
        
        self.spotify_data = {}
        self.player_details = {}
        
        ####################################################################
        
    def get_oauth2_url(self) -> str:
        scopes = ["user-read-playback-state", "user-modify-playback-state", "user-read-currently-playing", "user-read-private", "user-read-email"]
        
        url = requests.Request("GET", self.AUTH_ENDPOINT, params={
            "client_id": self.CLIENT_ID,
            "response_type": "code",
            "redirect_uri": self.REDIRECT_URI,
            "scope": " ".join(scopes)
        }).prepare().url
        
        self.spotify_data["is_authenticated"] = True
        
        return url
    
    def get_or_refresh_access_token(self, _type = None, auth_code = None) -> None:
        auth_string = self.CLIENT_ID + ":" + self.CLIENT_SECRET
        auth_base64 = str(base64.b64encode(auth_string.encode("utf-8")), "utf-8")
        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content": "application/x-www-form-urlencoded"
        }
        
        if _type == "GET" and auth_code is not None:
            data = {
                "code": auth_code,
                "grant_type": "authorization_code",
                "redirect_uri": self.REDIRECT_URI 
            }
        else:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.spotify_data['refresh_token']
            }
    
        response = requests.post(self.GET_TOKEN_ENDPOINT, headers=headers, data=data).json()
        
        self.spotify_data["expires_in"]     = datetime.now() + timedelta(seconds=response.get("expires_in"))
        self.spotify_data["access_token"]   = response.get("access_token")
        try:
            self.spotify_data["refresh_token"]  = response.get("refresh_token")
        except:
            pass
        self.spotify_data['is_authenticated'] = True
    
    def is_authenticated(self) -> bool:
        if not "is_authenticated" in self.spotify_data:
            return False
        return True
    
    def is_token_expired(self) -> bool:
        if not "expires_in" in self.spotify_data or self.spotify_data['expires_in'] <= datetime.now():
            return True
        return False
    
    def search_song(self, search_str: str = None):
        headers = {
            "Authorization": f"Bearer {self.spotify_data['access_token']}"
        }
        params = {
            "q": search_str,
            "type": "track",
            "limit": 5,
        }
        
        response = requests.get(self.API_ENDPOINT + "search", params=params, headers=headers).json()['tracks']['items']
        
        details = []
        
        for i in range(len(response)):
            song_details = {}
            song_details['uri']      = response[i]['uri']
            song_details["name"]     = response[i]['name'].replace('"',"")
            song_details['image']    = response[i]['album']['images'][0]['url']
            song_details['preview']  = response[i]['preview_url']
            song_details['duration'] = response[i]['duration_ms']
            song_details['artists']  = []
            for j in range(len(response[i]['album']['artists'])):
                song_details['artists'].append(response[i]['album']['artists'][j]['name'])
            details.append(song_details)
            
        return details
    
    def play_resume_song(self, uris, progress):
        headers = {
            "Authorization": f"Bearer {self.spotify_data['access_token']}",
            "Content-Type": "application/json"
        }
        data = {
            "uris": [uri for uri in uris],
            "position_ms": progress
        }
        
        response = requests.put(self.API_ENDPOINT + "me/player/play", json=data, headers=headers)
        print(response.text)
        
    def pause_song(self):
        headers = {
            "Authorization": f"Bearer {self.spotify_data['access_token']}"
        }
        response = requests.put(self.API_ENDPOINT + "me/player/pause", headers=headers)
        print(response.text)
        
    def get_current_playing_track(self):
        headers = {
            "Authorization": f"Bearer {self.spotify_data['access_token']}"
        }
        response = requests.get(self.API_ENDPOINT + "me/player/currently-playing", headers=headers).json()
        return response['progress_ms']
        

recommender = MusicRecommend()
    

@api.route("/search/<name>")
def search_song(name):
    from musicf.routes import spotify
    results = spotify.search_song(name)
    return jsonify({"results":results})


@api.route("/get_play", methods=['GET', 'POST'])
def fetch_details():
    if request.method == 'POST':
        from musicf.routes import spotify
        song_details = request.get_json()
        spotify.player_details['current'] = {}
        spotify.player_details['current']['name'] = song_details['name']
        spotify.player_details['current']['artists'] = song_details['artists']
        spotify.player_details['current']['img'] = song_details['img_url']
        spotify.player_details['current']['uri'] = song_details['uri']
        time_in_seconds = (int(song_details['duration']) // 1000)
        time_in_minutes = f"{time_in_seconds // 60}" + ":" +( f"{time_in_seconds % 60}" if (time_in_seconds % 60) >= 10 else f"0{time_in_seconds % 60}")
        spotify.player_details['current']['duration'] = time_in_minutes
        return redirect(url_for("play_music"))
    


@api.route("/play-resume", methods=['GET', 'POST'])
def play_resume():
    if request.method == 'POST':
        from musicf.routes import spotify
        song_details = request.get_json()
        spotify.play_resume_song(list(song_details['uri']), song_details['progress'])
        return None
    
    
@api.route("/pause")
def pause_music():
    from musicf.routes import spotify
    spotify.pause_song()
    return jsonify(spotify.get_current_playing_track())


@api.route("/get_recommendations/<name>")
def recommend(name):
    recommendations = recommender.recommend(name)
    from musicf.routes import spotify
    results = []
    for song in recommendations:
        details = spotify.search_song(f"{song['song_name']} {song['artist']}")
        results.append(details[0])
    return jsonify({"results": results})