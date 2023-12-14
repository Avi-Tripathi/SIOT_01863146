# spotify_manager.py
import requests
import random
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import mplcursors

class SpotifyManager:
    def __init__(self, token):
        self.token = token
        self.cluster_labels = None
        self.feature_values = None

    def get_saved_tracks(self, limit=50):
        # First, retrieve the total number of saved tracks for the user
        total_saved_tracks = self.get_total_saved_tracks()

        if total_saved_tracks is None:
            return []

        # Now, set the random offset within the range of the total saved tracks
        offset = random.randint(0, total_saved_tracks - limit)

        url = "https://api.spotify.com/v1/me/tracks"
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        params = {
            'market': 'ES',
            'limit': limit,
            'offset': offset
        }
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            tracks = [(item['track']['id'], item['track']['name'], [artist['name'] for artist in item['track']['artists']]) for item in data['items'] if item['track']['id']]
            return tracks
        else:
            print("Error getting saved tracks:", response.status_code)
            return []

    def get_total_saved_tracks(self):
        url = "https://api.spotify.com/v1/me/tracks"
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        params = {
            'limit': 1  # Only requesting 1 track to get the total count
        }
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            return data['total']
        else:
            print("Error getting total saved tracks:", response.status_code)
            return None
        
    def get_current_track(self):
        url = "https://api.spotify.com/v1/me/player/currently-playing"
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            track = response.json()
            return track['item']['id']
        else:
            print("Error getting currently playing track:", response.status_code)
            return None
        
    def play_track_in_spotify(self, track_id):
        url = f"https://api.spotify.com/v1/me/player/play"
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        params = {
            'uris': [f'spotify:track:{track_id}']
        }
        response = requests.put(url, headers=headers, json=params)

    def get_audio_features(self, track_ids, features):
        url = "https://api.spotify.com/v1/audio-features"
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        params = {
            'ids': ','.join(track_ids)
        }
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            feature_values = {item['id']: {feature: item[feature] for feature in features} for item in data['audio_features']}
            return feature_values
        else:
            print("Error getting audio features:", response.status_code)
            return {}

            
    def play_random_track_with_feature(self, feature, target_value, tolerance=0.1, max_attempts=10):
            for _ in range(max_attempts):
                tracks = self.get_saved_tracks()
                if tracks:
                    track_ids, track_names, track_artists = zip(*tracks)

                    feature_values = self.get_audio_features(track_ids, feature)

                    eligible_tracks = [(id, name, artists, value) for id, name, artists, value in zip(track_ids, track_names, track_artists, feature_values.values()) if
                                    (target_value - tolerance) <= value <= (target_value + tolerance)]

                    if eligible_tracks:
                        print(f"Eligible tracks with {feature} around {target_value}:")
                        for i, (track_id, track_name, track_artists, _) in enumerate(eligible_tracks, start=1):
                            print(f"{i}. Track: {track_name}")
                            print(f"   Artist(s): {', '.join(track_artists)}")

                        random_track_id, random_track_name, random_track_artists, _ = random.choice(eligible_tracks)
                        print("\nPlaying a random track from the eligible tracks:")
                        print(f"Track: {random_track_name}")
                        print(f"Artist(s): {', '.join(random_track_artists)}")
                        # You can add code to open the track in your preferred music player or Spotify client
                        self.play_track_in_spotify(random_track_id)
                        break  # Exit the loop when an eligible track is found
                    else:
                        print(f"No tracks found with {feature} around {target_value}")
                else:
                    print("No saved tracks available")

    def plot_tracks_on_graph(self, feature1, feature2, num_clusters):
        tracks = self.get_saved_tracks()
        if not tracks:
            print("No saved tracks available")
            return

        track_ids, track_names, track_artists = zip(*tracks)
        feature_values = self.get_audio_features(track_ids, [feature1, feature2])

        values1 = [feature_values[track_id][feature1] for track_id in track_ids]
        values2 = [feature_values[track_id][feature2] for track_id in track_ids]

        # Combine feature values into a numpy array
        feature_matrix = np.array(list(zip(values1, values2)))

        # Scale the feature values
        # Apply K-Means clustering
        kmeans = KMeans(n_clusters=num_clusters)
        kmeans.fit(feature_matrix)
        cluster_labels = kmeans.predict(feature_matrix)

        self.cluster_labels = cluster_labels
        self.feature_values = feature_values

        plt.figure(figsize=(10, 6))
        scatter = plt.scatter(values1, values2, c=cluster_labels, cmap='rainbow', alpha=0.5)
        plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=300, c='black', marker='X', label='Centroids')

        plt.title(f'Spotify Tracks with {num_clusters} Clusters')
        plt.xlabel(feature1)
        plt.ylabel(feature2)

        # Annotate the plot with track names (hidden by default)
        labels = [f"{i}. {label}" for i, label in enumerate(track_names, start=1)]
        mplcursors.cursor(hover=True).connect("add", lambda sel: sel.annotation.set_text(labels[sel.target.index]))

        plt.legend()
        plt.show()