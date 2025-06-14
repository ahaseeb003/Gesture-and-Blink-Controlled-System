import cv2 # OpenCV library for computer vision tasks
import mediapipe as mp # MediaPipe library for pre-built ML solutions (FaceMesh, Hands)
import math # For mathematical operations like euclidean distance
import time # For time-related operations, especially for blink detection timing
import platform # To detect the operating system for platform-specific functionalities

# Import platform-specific libraries for volume and brightness control
if platform.system() == "Windows":
    # pycaw for Windows audio control
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    # screen_brightness_control for Windows brightness control
    import screen_brightness_control as sbc
elif platform.system() == "Linux":
    # screen_brightness_control for Linux brightness control
    import screen_brightness_control as sbc

# Initialize MediaPipe FaceMesh and Hands models
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils # Utility for drawing landmarks

# Eye landmark indices for MediaPipe FaceMesh
# These points are crucial for calculating the Eye Aspect Ratio (EAR)
# L_EYE_POINTS: Indices for the left eye landmarks
L_EYE_POINTS = [33, 160, 158, 133, 153, 144] 
# R_EYE_POINTS: Indices for the right eye landmarks
R_EYE_POINTS = [362, 387, 385, 263, 373, 380] 

# Function to calculate Euclidean distance between two points
def euclidean_distance(point1, point2):
    # Calculates the straight-line distance between two points in a 2D plane
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

# Function to calculate Eye Aspect Ratio (EAR)
# EAR is a ratio of distances between eye landmarks, used to determine if an eye is open or closed
def eye_aspect_ratio(eye_landmarks):
    # Vertical distances between specific eye landmarks
    A = euclidean_distance(eye_landmarks[1], eye_landmarks[5])
    B = euclidean_distance(eye_landmarks[2], eye_landmarks[4])
    # Horizontal distance between specific eye landmarks
    C = euclidean_distance(eye_landmarks[0], eye_landmarks[3])

    # EAR formula
    ear = (A + B) / (2.0 * C)
    return ear

# Blink detection variables
blink_counter = 0 # Counts consecutive frames where eye is closed
blink_start_time = 0 # Records the time of the first blink in a sequence
BLINK_THRESHOLD = 0.25  # Threshold for EAR to consider an eye closed (adjust as needed)
BLINK_TIME_THRESHOLD = 0.5 # Time in seconds to detect a double blink

# Global variable for Selenium WebDriver
driver = None

# Function to open YouTube and play music using Selenium
def open_youtube_and_play_music():
    global driver
    if driver is None:
        print("Opening YouTube and playing music...")
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service as ChromeService
            from webdriver_manager.chrome import ChromeDriverManager

            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)
            driver.get("https://www.youtube.com/results?search_query=relaxing+music") 
            time.sleep(3)
            video_element = driver.find_element("id", "video-title")
            video_element.click()
            print("Playing music on YouTube.")
        except Exception as e:
            print(f"Error opening YouTube: {e}")
            driver = None # Reset driver if an error occurs
    else:
        print("YouTube window already open. Closing it.")
        driver.quit()
        driver = None

def main():
    global blink_counter, blink_start_time

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    if platform.system() == "Windows":
        devices = AudioUtilities.GetSpeakers()
        interface = cast(devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None), POINTER(IAudioEndpointVolume))
        volume = interface

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as face_mesh:
        with mp_hands.Hands(
            max_num_hands=2, # Allow detection of two hands
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as hands:

            while cap.isOpened():
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    continue

                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                face_results = face_mesh.process(image)
                hand_results = hands.process(image)

                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if face_results.multi_face_landmarks:
                    for face_landmarks in face_results.multi_face_landmarks:
                        mp_drawing.draw_landmarks(
                            image=image,
                            landmark_list=face_landmarks,
                            connections=mp_face_mesh.FACEMESH_TESSELATION,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1))

                        left_eye_coords = [face_landmarks.landmark[i] for i in L_EYE_POINTS]
                        right_eye_coords = [face_landmarks.landmark[i] for i in R_EYE_POINTS]

                        left_ear = eye_aspect_ratio(left_eye_coords)
                        right_ear = eye_aspect_ratio(right_eye_coords)
                        avg_ear = (left_ear + right_ear) / 2.0

                        if avg_ear < BLINK_THRESHOLD:
                            if blink_counter == 0:
                                blink_start_time = time.time()
                            blink_counter += 1
                        else:
                            if blink_counter > 0:
                                current_time = time.time()
                                if (current_time - blink_start_time) < BLINK_TIME_THRESHOLD and blink_counter >= 2: 
                                    open_youtube_and_play_music()
                                blink_counter = 0

                if hand_results.multi_hand_landmarks:
                    for idx, hand_landmarks in enumerate(hand_results.multi_hand_landmarks):
                        mp_drawing.draw_landmarks(
                            image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                        # Determine if it's a left or right hand
                        handedness = hand_results.multi_handedness[idx].classification[0].label

                        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                        index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                        distance = euclidean_distance(thumb_tip, index_finger_tip)

                        min_dist = 0.02
                        max_dist = 0.2

                        if handedness == "Left": # Control Volume with Left Hand
                            volume_level = int(100 * (distance - min_dist) / (max_dist - min_dist))
                            volume_level = max(0, min(100, volume_level))
                            if platform.system() == "Windows":
                                min_vol = -65.25
                                max_vol = 0.0
                                pycaw_volume = min_vol + (volume_level / 100) * (max_vol - min_vol)
                                volume.SetMasterVolumeLevel(pycaw_volume, None)
                                cv2.putText(image, f"Volume: {volume_level}%", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                        elif handedness == "Right": # Control Brightness with Right Hand
                            brightness_level = int(100 * (distance - min_dist) / (max_dist - min_dist))
                            brightness_level = max(0, min(100, brightness_level))
                            sbc.set_brightness(brightness_level)
                            cv2.putText(image, f"Brightness: {brightness_level}%", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                cv2.imshow("MediaPipe FaceMesh and Hands", image)

                if cv2.waitKey(5) & 0xFF == 27:
                    break

    cap.release()
    cv2.destroyAllWindows()
    if driver: # Ensure browser is closed on exit
        driver.quit()

if __name__ == \'__main__\':
    main()

