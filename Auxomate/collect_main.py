from statistics import mode
import time
from Recognitions.face_detect import FaceRecognition
from spotify.spotify_manager import SpotifyClient
from Recognitions.person_detection import PersonCounter
from data_analysis.data_logger import DataLogger

if __name__ == '__main__':
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
            current_time = time.time()
            if current_time - last_log_time >= 120:  # Check if 2 minutes (120 seconds) have passed since the last log
                last_log_time = current_time  # Update the last log time

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

                # Initialize variables to track if each user is playing a song
                avi_playing = False
                sarthak_playing = False

                # Check if 'Avi' is playing a song
                if person_id == "Both" or person_id == "Avi":
                    Spotify.call_refresh("Avi")
                    avi_current_track = Spotify.get_currently_playing()
                    if avi_current_track is not None:
                        avi_playing = True

                # Check if 'Sarthak' is playing a song
                if person_id == "Both" or person_id == "Sarthak":
                    Spotify.call_refresh("Sarthak")
                    sarthak_current_track = Spotify.get_currently_playing()
                    if sarthak_current_track is not None:
                        sarthak_playing = True

                # Determine the current track based on who is playing
                if avi_playing and not sarthak_playing:
                    current_track = avi_current_track
                elif sarthak_playing and not avi_playing:
                    current_track = sarthak_current_track
                else:
                    current_track = avi_current_track  # Set to Avi's track if both are playing or neither is playing
                # Now, you have 'current_track' set to Avi's track if both are playing. 

                data_logger.log_data(
                    time=time.strftime('%H:%M:%S', time.localtime()),
                    people=person_id,
                    avg_x=side,
                    current_track=current_track,
                )
                
                print (f"Person: {person_id}")
                print (f"Average Position: {side}")
                print (f"Current Track: {current_track}")
                print("Data logged successfully.")
                print("Waiting for 2 minutes before checking again...")
                time.sleep(120)  # Wait for 2 minutes before checking again

            else:
                # If less than 2 minutes have passed since the last log, wait for 5 seconds before checking again
                print("Less than 2 minutes since the last log. Waiting for 5 seconds before checking again...")
                time.sleep(5)
        else:
            # Zero people detected, wait for 5 seconds before checking again
            print("No person detected. Waiting for 5 seconds before checking again...")
            time.sleep(5)
