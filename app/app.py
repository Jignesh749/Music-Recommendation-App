import streamlit as st
from recommendation import recommend_similar_tracks
from playlist import create_playlist, recommend_tracks, sp, model, interaction_matrix

import seaborn as sns
from sklearn.metrics import silhouette_score

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import matplotlib.pyplot as plt


client_id = "716c1e25d0b94ad59424c2fe6e5268ec"
client_secret = "1f967480693941c69c6265ca6d920b4f"
redirect_uri = "http://localhost:8000/callback"
# Set up Streamlit application
st.title("Spotify AI Features")

scope = 'playlist-modify-private user-top-read user-library-read'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

# Music Recommendation
st.header("Music Recommendation")
track_id_recommendation = st.text_input("Enter a track ID for recommendation:")
if st.button("Recommend Tracks"):
    if track_id_recommendation:
        recommended_tracks = recommend_similar_tracks(track_id_recommendation)
        st.write("Recommended Tracks:")
        for track in recommended_tracks:
            st.write(f"{track['track_name']} by {track['artist_name']} (Track ID: {track['track_id']})")
    else:
        st.warning("Please enter a track ID.")


# Define the create_personalized_playlist function
def create_personalized_playlist():
    # Use the model to recommend tracks and create a playlist
    user_id = sp.current_user()['id']
    track_pool = interaction_matrix['track_id'].unique()
    recommended_track_ids = recommend_tracks(model, user_id, track_pool)

    # Create the playlist with recommended tracks
    playlist_name = "Personalized Playlist"
    playlist = create_playlist(sp, playlist_name, recommended_track_ids)

    # Check if the playlist was successfully created
    if 'id' in playlist:
        playlist_id = playlist['id']
        st.write(f"Playlist created: {playlist['name']} (ID: {playlist_id})")

        # Retrieve the tracks in the newly created playlist
        playlist_tracks = sp.playlist_items(playlist_id)
        track_names = [f"- {item['track']['name']} by {', '.join(artist['name'] for artist in item['track']['artists'])}" for item in playlist_tracks['items']]
        return playlist_id, track_names
    else:
        return None, None

# Create Personalized Playlist
if st.button("Create Personalized Playlist"):
    # Call create_personalized_playlist function
    playlist_id, track_names = create_personalized_playlist()
    
    # Check if the function returned a playlist ID
    if playlist_id:
        st.write(f"Personalized playlist created with ID: {playlist_id}")
        
        # Display the track names
        st.write("Track names added to the personalized playlist:")
        for name in track_names:
            st.write(name)
    else:
        st.warning("Failed to create a personalized playlist.")


