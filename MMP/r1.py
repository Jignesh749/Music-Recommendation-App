import spotipy
from spotipy.oauth2 import SpotifyOAuth
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
import numpy as np

# Set up Spotify OAuth with the necessary scope and client ID
scope = "user-top-read user-library-read"  # Include both user-top-read and user-library-read scopes
client_id = "716c1e25d0b94ad59424c2fe6e5268ec"
client_secret = "1f967480693941c69c6265ca6d920b4f"
redirect_uri = "http://localhost:8000/callback"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, open_browser=False, cache_path=".spotify_cache"))

# Function to create a user's feature vector
def create_user_feature_vector(user_id):
    try:
        # Get user's top tracks
        top_tracks = sp.current_user_top_tracks(limit=50, offset=0, time_range='medium_term')
        track_ids = [track['id'] for track in top_tracks['items']]
        
        # Get audio features for user's top tracks
        audio_features = sp.audio_features(track_ids)
        
        # Filter out None values
        audio_features = [track for track in audio_features if track is not None]

        # Extract relevant audio features
        features = np.array([[
            track['danceability'], 
            track['energy'], 
            track['loudness'], 
            track['speechiness'], 
            track['acousticness'], 
            track['instrumentalness'], 
            track['liveness'], 
            track['valence']
        ] for track in audio_features])
        
        # Standardize features
        scaler = StandardScaler()
        features_standardized = scaler.fit_transform(features)
        
        # Reduce dimensionality with PCA
        pca = PCA(n_components=3)
        features_pca = pca.fit_transform(features_standardized)
        
        return features_pca.mean(axis=0)  # Return the mean of the PCA-transformed features
    
    except Exception as e:
        print("Error creating user feature vector:", e)
        return None

# Function to get recommendations for the user using collaborative filtering
def get_recommendations(user_id):
    try:
        # Create user's feature vector
        user_feature_vector = create_user_feature_vector(user_id)
        if user_feature_vector is None:
            return []

        # Get seed tracks based on the user's top tracks
        top_tracks = sp.current_user_top_tracks(limit=5, offset=0, time_range='medium_term')
        seed_tracks = [track['id'] for track in top_tracks['items']]

        # Get recommendations from Spotify
        recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=5)
        recommended_tracks = recommendations['tracks']

        # Get recommended track names
        recommended_track_names = [track['name'] for track in recommended_tracks]

        return recommended_track_names

    except Exception as e:
        print("Error getting recommendations:", e)
        return []

# Example usage
user_id = '31r4azd7bd3b5pvitrb76akubrru'
recommendations = get_recommendations(user_id)
print("Recommended track names:", recommendations)
