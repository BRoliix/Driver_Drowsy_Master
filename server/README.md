The code utilizes the shape_predictor_68_face_landmarks.dat model to detect the eyes' position and determine if they are open or closed. If the eyes remain closed for over 10 seconds, an alarm is triggered to alert the user. Additionally, the system sends an SOS signal to the database, which can be viewed by the administrator through a website interface.

To achieve this functionality, the code employs computer vision techniques to identify facial landmarks, particularly focusing on the eyes. By analyzing the spatial arrangement of these landmarks, the code can ascertain whether the eyes are open or closed.

If the eyes are detected as closed for a continuous duration exceeding 10 seconds, the system activates an alarm to notify the user, thereby preventing potential hazards due to prolonged eye closure, such as drowsiness or fatigue.

Furthermore, to ensure safety and facilitate monitoring, the system sends an SOS signal to a centralized database. This signal contains relevant information indicating the occurrence of prolonged eye closure. The database stores these SOS signals, allowing the administrator to access and review them through a dedicated website interface.

By integrating these functionalities, the system enhances user safety by providing timely alerts for extended periods of eye closure and enables efficient monitoring and management of critical events through the centralized database and web-based administration interface.
