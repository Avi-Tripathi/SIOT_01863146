from ultralytics import YOLO
import cv2
from statistics import mode
import time

class PersonCounter:
    def __init__(self, model_path='yolov8n.pt'):
        self.model = YOLO(model_path)

    def mode_side_of_screen(self, duration):
        cap = cv2.VideoCapture(0)
        start_time = time.time()
        frame_count = 0
        people_counts = []
        side_counts = []
        most_common_people_count = None
        most_common_side = None

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            results = self.model(frame, agnostic_nms=True)[0]
            left_count = 0
            right_count = 0
            person_count = 0

            for result in results:
                detection_count = result.boxes.shape[0]

                for i in range(detection_count):
                    cls = int(result.boxes.cls[i].item())
                    name = result.names[cls]

                    if name == 'person':
                        person_count += 1
                        confidence = float(result.boxes.conf[i].item())
                        bounding_box = result.boxes.xyxy[i].cpu().numpy()
                        x_center = (bounding_box[0] + bounding_box[2]) / 2  # Calculate the center of the bounding box

                        if x_center < frame.shape[1] / 2:  # Check if the center is on the left side
                            left_count += 1
                            side = 'left'
                        else:
                            right_count += 1
                            side = 'right'

                        x = int(bounding_box[0])
                        y = int(bounding_box[1])
                        width = int(bounding_box[2] - x)
                        height = int(bounding_box[3] - y)

                        cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 0), 2)
                        cv2.putText(frame, f'{name} ({confidence:.2f}) - {side}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            side = None
            if left_count > 0 and right_count == 0:
                side = 'left'
            elif right_count > 0 and left_count == 0:
                side = 'right'
            elif left_count > 0 and right_count > 0:
                side = 'both'

            side_counts.append(side)
            people_counts.append(person_count)

            cv2.imshow('frame', frame)
            frame_count += 1

            cv2.waitKey(1)
            if time.time() - start_time >= duration:
                break

        cap.release()
        cv2.destroyAllWindows()

        if people_counts:

            most_common_people_count = mode(people_counts)
            most_common_side = mode(side_counts)

        return most_common_people_count, most_common_side

# Example usage:
if __name__ == '__main__':
    person_counter = PersonCounter()
    duration_seconds = 400  # Change the desired duration in seconds

    people_count, side = person_counter.mode_side_of_screen(duration_seconds)
    print(f"Most common people detected per frame: {people_count}")
    print(f"Most common side of the screen: {side}")
