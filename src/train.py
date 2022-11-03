import uuid
import os
import time
import cv2

img_path = os.path.join("data", "images")
labels = ["R_hand", "L_hand"]
number_imgs = 10


def cap_img():
    cap = cv2.VideoCapture(0)
    for label in labels:
        print(label)
        time.sleep(5)
        for number_img in range(number_imgs):
            print(f"Collecting image for {label}, number: {str(number_img)}")
            ret, frame = cap.read()
            h_flip = cv2.flip(frame, 1)
            img_name = os.path.join(img_path, f"{label}-{str(uuid.uuid1())}.jpg")
            cv2.imwrite(img_name, h_flip)
            cv2.imshow("Image Collection", h_flip)
            time.sleep(2)
            if cv2.waitKey(10) & 0xFF == ord("q"):
                break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # pipenv run python yolov5/train.py --img 640 --batch 16 --epochs 300 --data yolov5/dataset.yaml --weights yolov5/yolov5s.pt
    cap_img()
