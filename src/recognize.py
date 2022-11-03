import torch
import os
import numpy as np
import cv2
import mediapipe as mp
import time

# default_model = torch.hub.load("ultralytics/yolov5", "yolov5s")
root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
hama_model = torch.hub.load(
    "ultralytics/yolov5",
    "custom",
    path=f"{root_path}/models/hama_best.pt",
)
type_model = torch.hub.load(
    "ultralytics/yolov5", "custom", path=f"{root_path}/models/best.pt"
)
camera = cv2.VideoCapture()
record_hand = None
object_id = 0
recognize_results = []


def control_camera(switch):
    # turn on/off camera
    global camera
    if switch == "open":
        camera = cv2.VideoCapture(0)
    elif switch == "close":
        camera.release()
        # cv2.destroyAllWindows()


def detect():
    global camera
    try:
        while camera.isOpened():
            _, frame = camera.read()
            hand_coordinates = track_hands(frame)
            if hand_coordinates is not None:
                # return detect area
                x_min = int(hand_coordinates["x_hand"]) - 200
                y_min = int(hand_coordinates["y_hand"]) - 200
                if x_min < 0:
                    x_min = 0
                elif y_min < 0:
                    y_min = 0

                upper_left = (x_min, y_min)
                bottom_right = (
                    int(hand_coordinates["x_hand"]) + 200,
                    int(hand_coordinates["y_hand"]) + 200,
                )
                cv2.rectangle(frame, upper_left, bottom_right, (100, 50, 200), 5)
                rect_frame = frame[
                    upper_left[1] : bottom_right[1], upper_left[0] : bottom_right[0]
                ]

                yolo_recognition(rect_frame)

                # Replacing the image on Region of Interest
                # frame[
                #     upper_left[1] : bottom_right[1], upper_left[0] : bottom_right[0]
                # ] = recognition_rect
            _, buffer = cv2.imencode(".jpg", cv2.flip(frame, 1))
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
    except NameError:
        pass


def yolo_recognition(rect_img):
    global recognize_results
    global object_id
    local_time = time.localtime()
    time_format = time.strftime("%H:%M:%S", local_time)
    models = [
        {"name": "hama", "model": hama_model},
        {"name": "type", "model": type_model},
    ]
    for model in models:
        results = model["model"](rect_img)
        object = results.pandas().xyxy[0]["name"]
        confidence = results.pandas().xyxy[0]["confidence"]
        if len(object) >= 1:
            search = next(
                (
                    i
                    for i, item in enumerate(recognize_results)
                    if item["ID"] == object_id
                ),
                None,
            )

            object_data = {
                "model": model["name"],
                "meaning": object.to_dict()[0],
                "confidence": confidence.to_dict()[0],
            }

            if search is not None:
                search_model = next(
                    (
                        i
                        for i, item in enumerate(recognize_results[search]["objects"])
                        if item["model"] == model["name"]
                    ),
                    None,
                )

                if (
                    search_model is not None
                    and recognize_results[search]["objects"][search_model]["confidence"]
                    < confidence.to_dict()[0]
                ):
                    recognize_results[search]["objects"][search_model] = object_data
                if search_model is None:
                    recognize_results[search]["objects"].append(object_data)
            if search is None:
                recognize_results.append(
                    {"ID": object_id, "time": time_format, "objects": [object_data]}
                )


#     # return np.squeeze(results.render())


def track_hands(frame):
    # Get video size
    global record_hand
    global object_id
    frame_height, frame_width, _ = frame.shape
    # Get hand coordinates
    mp_hands = mp.solutions.hands

    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        max_num_hands=1,
    ) as hands:
        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame)
        # if results.multi_hand_landmarks:
        #     for hand_landmarks in results.multi_hand_landmarks:
        #         # Calculate the coordinates of the hand
        #         return {
        #             "x_hand": hand_landmarks.landmark[
        #                 mp_hands.HandLandmark.INDEX_FINGER_TIP
        #             ].x
        #             * frame_width,
        #             "y_hand": hand_landmarks.landmark[
        #                 mp_hands.HandLandmark.INDEX_FINGER_TIP
        #             ].y
        #             * frame_height,
        #         }
        if results.multi_handedness is None:
            which_hand = None
        else:
            which_hand = results.multi_handedness[0].classification[0].label

        if which_hand is None or which_hand != record_hand:
            record_hand = which_hand
            if len(recognize_results) != object_id:
                object_id = object_id + 1

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Calculate the coordinates of the hand
                return {
                    "x_hand": hand_landmarks.landmark[
                        mp_hands.HandLandmark.INDEX_FINGER_TIP
                    ].x
                    * frame_width,
                    "y_hand": hand_landmarks.landmark[
                        mp_hands.HandLandmark.INDEX_FINGER_TIP
                    ].y
                    * frame_height,
                }


def detect_area(coordinates, frame):
    # return detect area
    upper_left = (
        int(coordinates["x_hand"]) - 250,
        int(coordinates["y_hand"]) - 250,
    )
    bottom_right = (
        int(coordinates["x_hand"]) + 250,
        int(coordinates["y_hand"]) + 250,
    )
    cv2.rectangle(frame, upper_left, bottom_right, (100, 50, 200), 5)
    return frame[upper_left[1] : bottom_right[1], upper_left[0] : bottom_right[0]]


def test():
    camera = cv2.VideoCapture(f"{root_path}/HamaBeadsID/Video_clean.mp4")
    while camera.isOpened():
        _, frame = camera.read()
        results = model(frame)
        cv2.imshow("YOLOv5", np.squeeze(results.render()))
        if cv2.waitKey(10) & 0xFF == ord("q"):
            break
    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    test()
