import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import joblib
import pandas as pd
from playlist import get_user_tracks, get_user_top_tracks, create_interaction_matrix, recommend_tracks, create_playlist

# Define the scope of access
scope = "user-library-read playlist-modify-public user-top-read playlist-modify-private"

# Set up page configuration
st.set_page_config(page_title="Spotify AI", page_icon="🎵")

# Authenticate with Spotify
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        redirect_uri="http://localhost:8501/",
        scope=scope,
    ))
except Exception as e:
    st.error(f"Failed to authenticate with Spotify: {e}")
    st.stop()

# Load the pre-trained model
try:
    model = joblib.load('playlist_recommender_model.joblib')
except Exception as e:
    st.error(f"Failed to load the model: {e}")
    st.stop()

# Set up the Streamlit application
st.title("Spotify AI 🎵")

# Retrieve user ID and provide a message if the user is not logged in
try:
    user_id = sp.current_user()['id']
except spotipy.exceptions.SpotifyException as e:
    st.warning("Please authenticate with Spotify to continue.")
    st.stop()

# Function to recommend and create a playlist
def recommend_and_create_playlist():
    try:
        with st.spinner("Fetching tracks and recommendations..."):
            # Retrieve user's tracks and top tracks
            user_tracks = get_user_tracks(sp, limit=20)
            top_tracks = get_user_top_tracks(sp, time_range='medium_term', limit=20)

            # Create an interaction matrix
            interaction_matrix = create_interaction_matrix(user_tracks, top_tracks)

            # Provide an input widget for the user to choose the number of recommendations
            num_recommendations = st.number_input(
                "Number of recommendations:", 
                min_value=1, 
                max_value=50, 
                value=20, 
                step=1
            )

            # Use the model to recommend tracks
            track_pool = interaction_matrix['track_id'].unique()
            recommended_track_ids = recommend_tracks(model, user_id, track_pool, num_recommendations=num_recommendations)

            # Create the playlist with recommended tracks
            playlist_name = "Recommended Playlist"

            # Try to create the playlist
            playlist = create_playlist(sp, playlist_name, recommended_track_ids)
            
            # Check if playlist creation was successful
            if playlist is not None:
                # Playlist created successfully
                st.success(f"Playlist created: {playlist['name']} (ID: {playlist['id']})")

                # Retrieve the tracks in the newly created playlist
                playlist_tracks = sp.playlist_items(playlist['id'])

                # Display the names of tracks in the playlist
                st.subheader("Track names in the newly created playlist:")
                for item in playlist_tracks['items']:
                    track = item['track']
                    track_name = track['name']
                    artist_names = ", ".join(artist['name'] for artist in track['artists'])
                    st.text(f"- {track_name} by {artist_names}")
            else:
                # If playlist creation failed, display an error message
                st.error("There was an error creating the playlist. Please check your permissions and try again.")

    except Exception as e:
        # Handle any exceptions
        st.error(f"An error occurred: {e}")

# Add a button to run the recommendation and playlist creation
if st.button("Recommend and Create Playlist 🎵"):
    recommend_and_create_playlist()
