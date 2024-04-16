import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
import joblib
import logging

print("Current working directory:", os.getcwd())

# Define the scope of access
scope = "user-library-read playlist-modify-public user-top-read playlist-modify-private"

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="716c1e25d0b94ad59424c2fe6e5268ec",
    client_secret="1f967480693941c69c6265ca6d920b4f",
    redirect_uri="http://localhost:8000/callback",
    scope=scope,
))

# Load the pre-trained model
# Construct the file path using os.path.join
model_path = os.path.join(os.path.dirname(__file__), 'playlist_recommender_model.joblib')
model = joblib.load(model_path)

# Function to get user tracks
def get_user_tracks(sp, limit=20):
    try:
        tracks = []
        results = sp.current_user_saved_tracks(limit=limit)
        while results:
            tracks.extend([item['track']['id'] for item in results['items']])
            if results['next']:
                results = sp.next(results)
            else:
                break
        return tracks
    except SpotifyException as e:
        logging.error(f"Error fetching user's saved tracks: {e}")
        return []

# Function to get user's top tracks
def get_user_top_tracks(sp, time_range='medium_term', limit=20):
    try:
        top_tracks = sp.current_user_top_tracks(time_range=time_range, limit=limit)
        return [track['id'] for track in top_tracks['items']]
    except SpotifyException as e:
        logging.error(f"Error fetching user's top tracks: {e}")
        return []

# Retrieve user tracks and top tracks
user_tracks = get_user_tracks(sp, limit=20)
top_tracks = get_user_top_tracks(sp, time_range='medium_term', limit=20)

# Create an interaction matrix
def create_interaction_matrix(user_tracks, top_tracks):
    user_id = sp.current_user()['id']
    data = {'user_id': user_id, 'track_id': user_tracks + top_tracks, 'rating': [3]*len(user_tracks) + [5]*len(top_tracks)}
    return pd.DataFrame(data)

interaction_matrix = create_interaction_matrix(user_tracks, top_tracks)

# Function to recommend tracks
def recommend_tracks(model, user_id, track_pool, num_recommendations=20):
    recommendations = [(track_id, model.predict(user_id, track_id).est) for track_id in track_pool]
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return [rec[0] for rec in recommendations[:num_recommendations]]

# Create a playlist
def create_playlist(sp, name, track_ids):
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user_id, name, public=True)
    sp.playlist_add_items(playlist['id'], track_ids)
    return playlist

# Use the model to recommend tracks and create a playlist
user_id = sp.current_user()['id']
track_pool = interaction_matrix['track_id'].unique()
recommended_track_ids = recommend_tracks(model, user_id, track_pool)

# Create the playlist with recommended tracks
playlist_name = "Recommended Playlist"
playlist = create_playlist(sp, playlist_name, recommended_track_ids)
print(f"Playlist created: {playlist['name']} (ID: {playlist['id']})")

# Retrieve the tracks in the newly created playlist
playlist_tracks = sp.playlist_items(playlist['id'])

# Print the names of tracks in the playlist
print("\nTrack names in the newly created playlist:")
for item in playlist_tracks['items']:
    track = item['track']
    print(f"- {track['name']} by {', '.join(artist['name'] for artist in track['artists'])}")
