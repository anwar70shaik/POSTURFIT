import cv2
import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
import mediapipe as mp
import threading
from plyer import notification

# Initialize MediaPipe Pose for posture detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=2)

# Variables to track the last posture state and active slouch type
last_slouch_type = None

# Notification function
def send_notification(message):
    notification.notify(
        title="Posture Alert",
        message=message,
        timeout=3
    )

# Posture check function
def check_posture(landmarks):
    global last_slouch_type
    # Retrieve landmark points
    shoulder_left = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    shoulder_right = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    neck = landmarks[mp_pose.PoseLandmark.NOSE.value]
    hip_left = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    hip_right = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    # Define thresholds
    forward_threshold = 0.15
    shoulder_alignment_threshold = 0.05
    neck_height_threshold = 0.2
    # Calculate posture indicators
    shoulder_center_x = (shoulder_left.x + shoulder_right.x) / 2
    neck_x = neck.x
    forward_head_posture = abs(neck_x - shoulder_center_x) > forward_threshold
    shoulder_alignment = abs(shoulder_left.y - shoulder_right.y) < shoulder_alignment_threshold
    neck_y = neck.y
    hips_center_y = (hip_left.y + hip_right.y) / 2
    neck_too_low = neck_y > (hips_center_y - neck_height_threshold)
    # Determine slouch type
    if forward_head_posture and neck_too_low:
        current_slouch_type = "forward_slouch"
    elif not shoulder_alignment:
        current_slouch_type = "shoulders_misaligned"
    elif neck_too_low:
        current_slouch_type = "neck_down"
    else:
        current_slouch_type = None
    # Check for slouch type change
    if current_slouch_type != last_slouch_type:
        if current_slouch_type == "forward_slouch":
            send_notification("Tip: Keep your neck aligned with your shoulders to avoid forward slouching.")
        elif current_slouch_type == "shoulders_misaligned":
            send_notification("Tip: Keep shoulders at the same height to avoid slouching.")
        elif current_slouch_type == "neck_down":
            send_notification("Tip: Keep your neck upright to maintain good posture.")
        last_slouch_type = current_slouch_type  # Update last slouch type

    return current_slouch_type is not None

# Start posture detection
def start_posture_detection():
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        if results.pose_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            if check_posture(results.pose_landmarks.landmark):
                cv2.putText(frame, "Slouching Detected!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            else:
                cv2.putText(frame, "Good Posture", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow("Posture Detection", frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# Exercise data
exercises = {
    "Neck Pain Relief": {
        "name": "Neck Stretch",
        "description": "Gently tilt your head to one side, bringing your ear toward your shoulder. Hold for 15 seconds and switch sides.",
        "image_path": r"C:\\Users\\jyosh\\OneDrive\\Desktop\\AD 3-1\\POSTUREFIT\\stock-vector-neck-stretches-instructions-for-correct-head-and-shoulder-posture-outline-diagram-labeled-2301444907.jpg"  # Corrected image path
    },
    "Back Pain Relief": {
        "name": "Back Pain Pose",
        "description": "Kneel on the floor and stretch your arms forward, lowering your chest to your knees. Hold for 20 seconds.",
        "image_path": r"C:\\Users\\jyosh\\OneDrive\\Desktop\\AD 3-1\\POSTUREFIT\\moov_insta_v26_oo-min.jpg"  # Corrected image path
    }
}

# Function to show exercise details
def show_exercise(exercise):
    exercise_window = tk.Toplevel()
    exercise_window.title(exercise["name"])
    exercise_window.geometry("320x480")  # Mobile-sized window

    # Load and display exercise image
    try:
        exercise_image = Image.open(exercise["image_path"])  # Correct path usage
        exercise_image = exercise_image.resize((250, 150), Image.LANCZOS)  # Resize to fit window
        exercise_image = ImageTk.PhotoImage(exercise_image)

        image_label = tk.Label(exercise_window, image=exercise_image)
        image_label.image = exercise_image  # Keep a reference to prevent garbage collection
        image_label.pack(pady=10)
    except Exception as e:
        print(f"Error loading image: {e}")
        error_label = tk.Label(exercise_window, text="Error loading image.", fg="red")
        error_label.pack(pady=10)

    description_label = tk.Label(exercise_window, text=exercise["description"], wraplength=250)
    description_label.pack(pady=10)

    # Back button with left arrow symbol
    back_button = tk.Button(exercise_window, text="← Back", font=("Arial", 10), bg="#4CAF50", fg="white",
                            activebackground="#388E3C", activeforeground="white", width=10,
                            command=exercise_window.destroy)
    back_button.pack(pady=5, ipadx=10, ipady=5)

# Function to open Instant Exercises window
def open_instant_exercises():
    instant_exercises_window = tk.Toplevel()
    instant_exercises_window.title("Instant Exercises")
    instant_exercises_window.geometry("320x480")  # Mobile-sized window

    for category, exercise in exercises.items():
        exercise_button = tk.Button(instant_exercises_window, text=exercise["name"],
                                    font=("Arial", 12), bg="#FFC107", fg="white",
                                    activebackground="#FF9800", activeforeground="white",
                                    command=lambda ex=exercise: show_exercise(ex))
        exercise_button.pack(pady=10, ipadx=10, ipady=10)

    # Back button with left arrow symbol
    back_button = tk.Button(instant_exercises_window, text="← Back", font=("Arial", 10), bg="#4CAF50", fg="white",
                            activebackground="#388E3C", activeforeground="white", width=10,
                            command=instant_exercises_window.destroy)
    back_button.pack(pady=5, ipadx=10, ipady=5)

# Tkinter UI
def create_ui():
    root = tk.Tk()
    root.title("Posture Detection System")
    root.geometry("320x480")  # Mobile-sized window
    root.configure(bg="#F0F4F8")  # Light background color

    # Add Welcome Message with App Name
    welcome_label = tk.Label(root, text="Welcome to PostureFit", font=("Arial", 16, "bold"), fg="#4CAF50")
    welcome_label.pack(pady=20)

    # Load and display home page image
    home_image = Image.open("C:\\Users\\jyosh\\OneDrive\\Desktop\\AD 3-1\\POSTUREFIT\\logo1.png")  # Replace with your home page image path
    home_image = home_image.resize((300, 200), Image.LANCZOS)  # Resize to fit within the window
    home_image = ImageTk.PhotoImage(home_image)

    image_label = tk.Label(root, image=home_image)
    image_label.image = home_image  # Keep a reference to prevent garbage collection
    image_label.pack(pady=10)

    # Custom font for buttons
    button_font = font.Font(size=12, weight="bold")

    # Detect Posture Button
    detect_button = tk.Button(root, text="Detect Posture", font=button_font, bg="#4CAF50", fg="white",
                              activebackground="#388E3C", activeforeground="white",
                              command=lambda: threading.Thread(target=start_posture_detection).start())
    detect_button.pack(pady=20, ipadx=10, ipady=10)

    # Instant Exercises Button
    instant_exercises_button = tk.Button(root, text="Instant Exercises", font=button_font, bg="#FFC107", fg="black",
                                         activebackground="#FF9800", activeforeground="black",
                                         command=open_instant_exercises)
    instant_exercises_button.pack(pady=10, ipadx=10, ipady=10)

    # Exit Button
    exit_button = tk.Button(root, text="Exit", font=button_font, bg="#f44336", fg="white",
                            activebackground="#d32f2f", activeforeground="white", command=root.quit)
    exit_button.pack(pady=20, ipadx=10, ipady=10)

    root.mainloop()

# Run the UI
create_ui()
