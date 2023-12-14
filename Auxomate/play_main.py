import random
from statistics import mode
import time
from Recognitions.face_detect import FaceRecognition
from spotify.new_spotify import SpotifyClient
from Recognitions.person_detection import PersonCounter
from data_analysis.data_logger import DataLogger
from data_analysis.predictor import EnergyPredictor
from datetime import datetime

if __name__ == '__main__':
    predictor = EnergyPredictor('/Users/avitripathi/Documents/DE4/iot/the one/Auxomate/new_energy.csv')
    person_counter = PersonCounter()
    duration_seconds = 10  # Change the desired duration in seconds
    face_scan_interval = 10  # Face scan interval in seconds

    FaceRecognition = FaceRecognition()
    Spotify = SpotifyClient()
    data_logger = DataLogger()

    last_log_time = 0  # Initialize last log time to 0

    while True:
        people_count, side = person_counter.mode_side_of_screen(5)
        print(f"Most common people detected in a frame: {people_count}")
        person_id = None

        if people_count > 0:
                if people_count == 1:
                    # Exactly one person is detected, perform face scanning
                    print("Person detected. Starting face scan...")

                    # Perform face scanning every 'face_scan_interval' seconds
                    person_start_time = time.time()
                    x_positions = []  # List to collect x positions during scanning
                    scanning_duration = 30  # Set the scanning duration to 30 seconds

                    while time.time() - person_start_time < scanning_duration:
                        print("Scanning for the person's face...")
                        face = FaceRecognition.scan_faces(duration=face_scan_interval)

                        if face:
                            # Do something with the recognized people (e.g., print their names)
                            print(face)
                            person_id = face[0]
                            print(f"Person recognized: {person_id}")
                            break  # Exit the loop when someone is recognized
                        else:
                            print("No one recognized, continuing to analyze...")
                        time.sleep(3)

                    if person_id is None:
                        person_id = "unknown"
                        print("No one recognized after 30 seconds, setting person_id to 'unknown'.")

                else:
                    # Multiple people detected, log the data without including a face scan
                    person_id = "Both"
                    print("Both people detected. Skipping face scan and logging data...")

                # Check if 'Avi' is playing a song
                if person_id == "Both" or person_id == "Avi":
                    Spotify.call_refresh("Avi")
                    
                # Check if 'Sarthak' is playing a song
                if person_id == "Both" or person_id == "Sarthak":
                    Spotify.call_refresh("Sarthak")

                if person_id == "unknown":
                    Spotify.call_refresh("Avi")

                predictor.load_model()
                current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                energy = predictor.predict_energy(person_id,current_timestamp,side)
                track_ids = Spotify.find_eligible_songs('energy',energy, 0.1)
                status = Spotify.play_random_song(track_ids)

                
                last_song_queued_time = time.time()  # Initialize last queued time

                if status == 204:
                    print("Successfully queued a song.")

                    while people_count > 0:
                        remaining_time = Spotify.calculate_remaining_time()
                        print(remaining_time)
                        
                        if remaining_time < 30:
                            people_count, side = person_counter.mode_side_of_screen(5)
                            if people_count > 0:
                            # Check if enough time has passed since the last song was queued
                                print(time.time() - last_song_queued_time)

                                if time.time() - last_song_queued_time > 30:

                                    predictor.load_model()
                                    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    energy = predictor.predict_energy(person_id,current_timestamp,side)
                                    songs = Spotify.find_eligible_songs('energy', energy, 0.1)
                                    print(songs)
                                    queue_song = songs[random.randint(0,len(songs)-1)]
                                    # input random song from songs into queue
                                    print('queue song: ' + queue_song)
                                    Spotify.add_song_to_queue(queue_song)
                                    
                                    last_song_queued_time = time.time()  # Update last queued time
                                    Spotify.calculate_remaining_time()
                                    
                                else:
                                    print("Not Queueing Yet")
                                    time.sleep(10)
                        else:
                            time.sleep(10)
                            print("Not Queueing Yet")
                    
                else:
                    # Zero people detected, wait for 5 seconds before checking again
                    print("No person detected. Waiting for 5 seconds before checking again...")
                    time.sleep(5)
