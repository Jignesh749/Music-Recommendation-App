import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Initialize Spotipy client
client_credentials_manager = SpotifyClientCredentials(client_id='YOUR_CLIENT_ID',
                                                      client_secret='YOUR_CLIENT_SECRET')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Database initialization
def init_db():
    conn = sqlite3.connect('music.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS preferences
                 (user_id INTEGER, genre TEXT, artist TEXT, song TEXT)''')
    conn.commit()
    conn.close()

# Signup endpoint
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    conn = sqlite3.connect('music.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    return jsonify({"message": "Signup successful"})

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    conn = sqlite3.connect('music.db')
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    if user:
        return jsonify({"message": "Login successful", "user_id": user[0]})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# Preferences endpoint
@app.route('/preferences', methods=['POST'])
def add_preferences():
    data = request.get_json()
    user_id = data.get('user_id')
    genre = data.get('genre')
    artist = data.get('artist')
    song = data.get('song')
    conn = sqlite3.connect('music.db')
    c = conn.cursor()
    c.execute("INSERT INTO preferences (user_id, genre, artist, song) VALUES (?, ?, ?, ?)",
              (user_id, genre, artist, song))
    conn.commit()
    conn.close()
    return jsonify({"message": "Preferences added successfully"})

# Recommendation endpoint
@app.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    conn = sqlite3.connect('music.db')
    c = conn.cursor()
    c.execute("SELECT genre FROM preferences WHERE user_id=?", (user_id,))
    genres = [row[0] for row in c.fetchall()]
    conn.close()
    
    # Get recommended tracks based on user's preferred genres
    recommended_tracks = []
    for genre in genres:
        results = sp.recommendations(seed_genres=[genre], limit=5)
        for track in results['tracks']:
            recommended_tracks.append(track['name'] + ' by ' + track['artists'][0]['name'])
    
    return jsonify({"recommended_tracks": recommended_tracks})

@app.route('/')
def index():
    return 'Welcome to the Music Recommendation System'

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
