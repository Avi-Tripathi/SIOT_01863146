import csv
from spotify.new_spotify import SpotifyClient

class SpotifyDataUpdater:
    def __init__(self, csv_file, audio_feature):
        self.csv_file = csv_file
        self.audio_feature = audio_feature

    def update_csv(self):
        # Initialize SpotifyAPI with your Spotify token
        spotify_api = SpotifyClient()
        spotify_api.call_refresh('Avi')

        # Read the original CSV file
        with open(self.csv_file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            # Create a list to store new rows with added audio features
            new_rows = []
            track_ids = []  # Store the track IDs in batches

            for row in csv_reader:
                track_id = row['track_id']

                if track_id is not None and track_id != "None":
                    track_ids.append(track_id)

                    # If we have 100 track IDs, make a request and reset the track_ids list
                    if len(track_ids) == 100:
                        audio_data = spotify_api.get_audio_features(track_ids, self.audio_feature)
                        for track_id, audio_value in audio_data.items():
                            # Create a new row with an additional column for the specified audio feature
                            new_row = {
                                'time': row['time'],
                                'person': row['person'],
                                'position': row['position'],
                                'track_id': track_id,
                                self.audio_feature: audio_value
                            }
                            new_rows.append(new_row)
                        track_ids = []  # Reset the track_ids list

            # Handle any remaining track IDs (less than 100)
            if track_ids:
                audio_data = spotify_api.get_audio_features(track_ids, self.audio_feature)
                for track_id, audio_value in audio_data.items():
                    new_row = {
                        'time': row['time'],
                        'person': row['person'],
                        'position': row['position'],
                        'track_id': track_id,
                        self.audio_feature: audio_value
                    }
                    new_rows.append(new_row)

        # Write the new data with the added audio feature column to a new CSV file
        new_csv_file_name = f'new_{self.audio_feature}.csv'
        with open(new_csv_file_name, 'w', newline='') as new_csv_file:
            fieldnames = ['time', 'person', 'position', 'track_id', self.audio_feature]
            csv_writer = csv.DictWriter(new_csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(new_rows)

if __name__ == "__main__":
    # Example usage:
    updater = SpotifyDataUpdater('/Users/avitripathi/Documents/DE4/iot/the one/Auxomate/data.csv', 'energy')
    updater.update_csv()
