import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import pickle

class EnergyPredictor:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)
        self.data['time'] = pd.to_datetime(self.data['time'])  # Convert 'time' to Timestamp
        self.features = pd.get_dummies(self.data[['person', 'position']])
        self.features['time'] = (self.data['time'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')  # Convert 'time' to Unix timestamp
        self.target = self.data['energy']
        self.model = None

    def train_model(self):
        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            self.features, self.target, test_size=0.2, random_state=42
        )

        # Create a Random Forest Regressor model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)

        # Train the model
        self.model.fit(X_train, y_train)

        # Evaluate the model on the test set
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        print(f'Mean Squared Error on Test Set: {mse}')

    def save_model(self, model_path='energy_predictor_model.pkl'):
        # Save the trained model to a file using pickle
        with open(model_path, 'wb') as file:
            pickle.dump(self.model, file)
        print(f'Model saved to {model_path}')

    def load_model(self, model_path='energy_predictor_model.pkl'):
        # Load a pre-trained model from a file using pickle
        with open(model_path, 'rb') as file:
            self.model = pickle.load(file)
        print(f'Model loaded from {model_path}')

    def predict_energy(self, person, time, position):
        # Make predictions for a given person, time, and position
        input_data = pd.DataFrame({'person': [person], 'position': [position]})
        
        # Ensure consistent one-hot encoding with training data
        input_data_encoded = pd.get_dummies(input_data)
        missing_cols = set(self.features.columns) - set(input_data_encoded.columns)
        
        # Add missing columns with zeros
        for col in missing_cols:
            input_data_encoded[col] = 0
        
        # Convert 'time' to Unix timestamp
        input_data_encoded['time'] = (pd.to_datetime(time) - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
        
        # Ensure columns are in the same order as during training
        input_data_encoded = input_data_encoded[self.features.columns]
        
        energy_prediction = self.model.predict(input_data_encoded)
        return energy_prediction[0]

# Example usage:
# Create an instance of the EnergyPredictor class
energy_predictor = EnergyPredictor('/Users/avitripathi/Documents/DE4/iot/the one/Auxomate/new_energy.csv')

# Train the model (you only need to do this once unless your data changes)
energy_predictor.train_model()

# Save the trained model to a file as a pickle
energy_predictor.save_model()

# Load the pre-trained model from a file
energy_predictor.load_model()

# Make predictions
person = 'Avi'
time = '2023-11-25 00:04:52'
position = 'right'
predicted_energy = energy_predictor.predict_energy(person, time, position)
print(f'Predicted Energy: {predicted_energy}')
