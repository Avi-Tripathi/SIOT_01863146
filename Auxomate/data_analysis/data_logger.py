import pandas as pd
from pymongo import MongoClient
import certifi

class DataLogger:
    def __init__(self, db_name='Auxomate', collection_name='Fulham Park Data'):
        self.uri = "mongodb+srv://avi28tripathi:6UxIgGlguy257uiR@cluster0.jpz18nw.mongodb.net/?retryWrites=true&w=majority"
        self.client = MongoClient(self.uri, tlsCAFile=certifi.where())
        self.db_name = db_name
        self.collection_name = collection_name
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

    def log_data(self, time, people, avg_x, current_track):
        data = {
            'time': time,
            'person': people,
            'position': avg_x,
            'track_id': current_track,
        }

        self.collection.insert_one(data)

    def export_to_csv(self, file_path='exported_data.csv'):
        cursor = self.collection.find({})
        data_list = list(cursor)
        df = pd.DataFrame(data_list)

        df.to_csv(file_path, index=False)
        print(f'Data exported to {file_path}')

