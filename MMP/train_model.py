import spotipy
from spotipy.oauth2 import SpotifyOAuth
from sklearn.ensemble import RandomForestRegressor
import pickle

# Set up Spotify OAuth with the necessary scope and client ID
scope = "user-top-read user-library-read"  # Include both user-top-read and user-library-read scopes
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
redirect_uri = "http://localhost:8000/callback"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, open_browser=False, cache_path=".spotify_cache"))

# Function to fetch audio features for tracks
def get_audio_features(track_ids):
    try:
        audio_features = sp.audio_features(track_ids)
        if audio_features:
            return [track for track in audio_features if track is not None]  # Filter out None values
        else:
            return []
    except Exception as e:
        print("Error fetching audio features:", e)

# Function to train the machine learning model
def train_model(track_ids):
    # Fetch audio features for the tracks
    audio_features = get_audio_features(track_ids)
    
    # Extract features and labels
    X_train = [...]  # Features extracted from audio_features
    y_train = [...]  # Corresponding mixing parameters
    
    # Train the model
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X_train, y_train)
    
    # Save the trained model to a file
    with open("trained_model.pkl", "wb") as file:
        pickle.dump(model, file)

# Example usage
user_id = 'YOUR_USER_ID'
top_tracks = sp.current_user_top_tracks(limit=50, offset=0, time_range='medium_term')
track_ids = [track['id'] for track in top_tracks['items']]
train_model(track_ids)
