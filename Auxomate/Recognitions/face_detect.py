import cv2
import pickle
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import time

class FaceRecognition:
    def __init__(self, faces_data_path='Recognitions/face_data/faces_data.pkl', names_path='Recognitions/face_data/names.pkl'):
        self.facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        
        with open(names_path, 'rb') as w:
            self.LABELS = pickle.load(w)
        with open(faces_data_path, 'rb') as f:
            self.FACES = pickle.load(f)
        
        self.knn = KNeighborsClassifier(n_neighbors=5)
        self.knn.fit(self.FACES, self.LABELS)
    
    def scan_faces(self, duration):
        cap = cv2.VideoCapture(0)
        recognized_people = {}
        start_time = time.time()
        while True:
            
            ret, frame = cap.read()
            if not ret:
                break  # Break the loop if frame retrieval fails
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.facedetect.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                crop_img = frame[y:y+h, x:x+w, :]
                resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
                output = self.knn.predict(resized_img)
                person_name = str(output[0])
                
                recognized_people[person_name] = True
                
                cv2.putText(frame, person_name, (x, y - 15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 1)
            
            cv2.imshow("Frame", frame)
            cv2.waitKey(1)
            if time.time() - start_time >= duration:
                break

        cap.release()
        cv2.destroyAllWindows()
        
        return list(recognized_people.keys())

# Usage example:
if __name__ == '__main__':
    face_recognition = FaceRecognition()

    while True:
        recognized_people = face_recognition.scan_faces(60)
        print(recognized_people)
        time.sleep(5)
