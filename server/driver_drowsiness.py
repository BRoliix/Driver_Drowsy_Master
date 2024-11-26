import cv2
import numpy as np
import dlib
from imutils import face_utils
import pyglet
from datetime import datetime
import dao

def sound_alarm():
    try:
        music = pyglet.resource.media('alarm.wav')
        music.play()
        print("music length is : %f" % music.duration)
    except Exception as e:
        print(f"Error playing alarm: {e}")

def compute(ptA, ptB):
    dist = np.linalg.norm(ptA - ptB)
    return dist

def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)

    if (ratio > 0.25):
        return 2
    elif (ratio > 0.21 and ratio <= 0.25):
        return 1
    else:
        return 0

def exec():
    cap = cv2.VideoCapture(0)
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    sleep = 0
    drowsy = 0
    active = 0
    status = ""
    color = (0, 0, 0)
    last_alert_time = None
    ALERT_COOLDOWN = 30  # 30 seconds cooldown
    previous_status = ""

    while True:
        _, frame = cap.read()
        _, face_frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = detector(gray)
        if len(faces) == 0:  # Reset states when no face is detected
            sleep = 0
            drowsy = 0
            active = 0
            status = ""
            continue

        for face in faces:
            x1 = face.left()
            y1 = face.top()
            x2 = face.right()
            y2 = face.bottom()

            face_frame = frame.copy()
            cv2.rectangle(face_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            landmarks = predictor(gray, face)
            landmarks = face_utils.shape_to_np(landmarks)

            left_blink = blinked(landmarks[36], landmarks[37],
                                landmarks[38], landmarks[41], landmarks[40], landmarks[39])
            right_blink = blinked(landmarks[42], landmarks[43],
                                landmarks[44], landmarks[47], landmarks[46], landmarks[45])

            current_time = datetime.now()
            can_alert = (last_alert_time is None or 
                        (current_time - last_alert_time).total_seconds() > ALERT_COOLDOWN)

            if (left_blink == 0 or right_blink == 0):
                sleep += 1
                drowsy = 0
                active = 0
                if sleep > 6:
                    status = "SLEEPING !!!"
                    if status != previous_status or can_alert:
                        try:
                            sound_alarm()
                            dao.raise_sos()
                            last_alert_time = current_time
                        except Exception as e:
                            print(f"Error raising alert: {e}")
                    color = (255, 0, 0)

            elif (left_blink == 1 or right_blink == 1):
                sleep = 0
                active = 0
                drowsy += 1
                if drowsy > 6:
                    status = "Drowsy !"
                    if status != previous_status or can_alert:
                        try:
                            sound_alarm()
                            dao.raise_sos()
                            last_alert_time = current_time
                        except Exception as e:
                            print(f"Error raising alert: {e}")
                    color = (0, 0, 255)

            else:
                drowsy = 0
                sleep = 0
                active += 1
                if active > 6:
                    status = "Active :)"
                    color = (0, 255, 0)

            previous_status = status
            cv2.putText(frame, status, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

            for n in range(0, 68):
                (x, y) = landmarks[n]
                cv2.circle(face_frame, (x, y), 1, (255, 255, 255), -1)

        cv2.imshow("Frame", frame)
        cv2.imshow("Result of detector", face_frame)
        key = cv2.waitKey(1)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

def exec_program():
    try:
        exec()
    except Exception as e:
        print(f"Error in main program: {e}")

class Drowsy:
    if __name__ == "__main__":
        exec_program()