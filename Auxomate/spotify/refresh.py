import requests
import time

class Refresh:
    # Define user_profiles as a class variable
    user_profiles = {
        'Avi': {
            "spotify_user_id": "fihy6fbyb97qeqs7zhhqji2ib",
            "refresh_token": "AQDZNg1_nbV1o9JBPL0Tkv3oHGe49UmLJd-QcDCl49rgduF8Fqg69bcryk3OAqmQDxMp4K6Pec3S5JHX2wBMi4afO7nLI0panQkzEb-ar8f0hz3Ft9GB0V0GnAI3QWz3NOI"
        }
        # 'Sarthak': {
        #     "spotify_user_id": "sarthakdas",
        #     "refresh_token": "AQCIBmrcYtROb_QQBhsELrVUc9QcNPZui1EbSwZzfU6llKi5kM8mNysk6O8hiEei0bok4gfnAGCOS9F8RtCIj0p0bX28R7eyg7mrHrozeL8y_BZaH-QT93wzsOeL_HJi5xQ"
        # }
    }

    def __init__(self, user_id):
        self.user_id = user_id

    def refresh(self):
        if self.user_id in self.user_profiles:
            user_profile = self.user_profiles[self.user_id]
            refresh_token = user_profile["refresh_token"]
            base_64 = "MGJlYzBjMWM5NTYyNDNmMmFiMGE0ZmFiOGUyNGJkNDY6MmY2YzgwNzk2ZTg5NGFkYzg5OWRhMzdhYzU2MTBjM2E="

            query = "https://accounts.spotify.com/api/token"
            response = requests.post(
                query,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token
                },
                headers={
                    "Authorization": "Basic " + base_64
                }
            )
            response_json = response.json()
            
            print(f"Spotify User ID: {user_profile['spotify_user_id']}")

            return response_json.get("access_token")
        else:
            print(f"User {self.user_id} not found in user_profiles.")
            return None
