import cv2
import random
import mediapipe as mp
import pygame
import tkinter as tk
import sys

# Initialize constants and variables
width, height = 640, 480
kuromi_x, kuromi_y = width // 4, height // 2
gap = 150
pipes = []
score = 0
pipe_speed = 8
frame_rate = 60
pipe_gap = 20

# Initialize tkinter to get screen dimensions
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()

# Calculate the position X and Y to center the window
pos_x = screen_width // 2 - width // 2
pos_y = screen_height // 2 - height // 2

# Initialize webcam capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, frame_rate)

# Initialize Mediapipe for face detection
mp_face = mp.solutions.face_detection
face_detection = mp_face.FaceDetection()

# Initialize Pygame for audio and load audio files
pygame.mixer.init()
game_over_sound = pygame.mixer.Sound("game_over_music.wav")
main_menu_music = pygame.mixer.Sound("main_menu_music.wav")

# Load Kuromi image
kuromi_image = cv2.imread("sanrio1.png", -1)
kuromi_image = cv2.resize(kuromi_image, (40, 40))  # Resize the Kuromi image

# Replace the draw_bird function with draw_kuromi
def draw_kuromi(frame):
    # Calculate the coordinates to place the Kuromi image centered around kuromi_x and kuromi_y
    kuromi_x_position = kuromi_x - kuromi_image.shape[1] // 2
    kuromi_y_position = int(kuromi_y - kuromi_image.shape[0] // 2)

    # Create a mask for transparent pixels
    mask = kuromi_image[:, :, 3] == 0

    # Place the Kuromi image on the frame, ignoring transparent pixels
    frame[kuromi_y_position:kuromi_y_position + kuromi_image.shape[0],
    kuromi_x_position:kuromi_x_position + kuromi_image.shape[1]][~mask] = kuromi_image[:, :, :3][~mask]

# Function to draw pipes on frame
def draw_pipes(frame):
    pipe_color = (168, 132, 168)  # Pipe color (green)

    for pipe in pipes:
        # Calculate the dimensions and coordinates for the top and bottom pipes
        top_pipe_rect = (pipe[0], 0, 50, pipe[1])
        bottom_pipe_rect = (pipe[0], pipe[1] + gap, 50, height - (pipe[1] + gap))

        # Draw the top and bottom pipes using rectangles
        cv2.rectangle(frame, (top_pipe_rect[0], top_pipe_rect[1]),
                      (top_pipe_rect[0] + top_pipe_rect[2], top_pipe_rect[1] + top_pipe_rect[3]), pipe_color, -1)
        cv2.rectangle(frame, (bottom_pipe_rect[0], bottom_pipe_rect[1]),
                      (bottom_pipe_rect[0] + bottom_pipe_rect[2], bottom_pipe_rect[1] + bottom_pipe_rect[3]), pipe_color, -1)

# Function to move pipes and update score
def move_pipes():
    global score
    for pipe in pipes:
        pipe[0] -= pipe_speed
        if pipe[0] + 50 < 0:
            pipes.remove(pipe)
            score += 1

# Function to display the main menu
def main_menu():
    global pos_x, pos_y
    video_path = "out.mp4"  # Replace with the actual path to your video file
    cap = cv2.VideoCapture(video_path)
    cv2.waitKey(10000)
    pygame.mixer.Sound.play(main_menu_music, loops=-1)
    cv2.namedWindow("Main Menu")

    # Move the window to the centered position
    cv2.moveWindow('Main Menu', pos_x, pos_y - 25)

    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset video to the beginning for looping
            continue
        with open("high_score.txt", "r") as file:
            high_score = int(file.read())
        cv2.putText(frame, f"High Score: {high_score}", (width // 2 - 45, height // 2 + 60), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (18, 17, 17), 2)

        cv2.imshow("Main Menu", frame)

        key = cv2.waitKey(1)
        if key == ord('s'):
            pygame.mixer.Sound.stop(main_menu_music)
            cap.release()
            cv2.destroyWindow("Main Menu")
            break
        elif key == ord('q'):
            pygame.mixer.Sound.stop(main_menu_music)
            cap.release()
            cv2.destroyAllWindows()
            sys.exit()

# Run the main menu
main_menu()

# Function to pause the game
def pause():
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.putText(frame, "PAUSED", (width // 2 - 100, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(frame, "Press r to Resume", (width // 2 - 100, height // 2 - 40), cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 0, 0), 2)
        cv2.putText(frame, "Press q to Quit", (width // 2 - 100, height // 2 - 80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 0, 0), 2)
        cv2.imshow("Flappy Kuromi uwu", frame)

        if cv2.waitKey(1) & 0xFF == ord('r'):
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            sys.exit()
            
# Function to handle the game over screen
def game_over():
    global pos_x, pos_y
    video_path = "game_over.mp4"
    cap = cv2.VideoCapture(video_path)
    pygame.mixer.Sound.play(game_over_sound)
    cv2.namedWindow("Game Over")
    cv2.moveWindow("Game Over", pos_x, pos_y)
    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        with open("high_score.txt", "r") as file:
            high_score = int(file.read())
        cv2.putText(frame, f"High Score: {high_score}", (width // 2 - 30, height // 2 + 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (15, 17, 17), 2)

        cv2.imshow("Game Over", frame)

        key = cv2.waitKey(1)
        if key == ord('r'):
            pygame.mixer.Sound.stop(game_over_sound)
            cap.release()
            cv2.destroyWindow("Game Over")
            break
        elif key == ord('q'):
            pygame.mixer.Sound.stop(main_menu_music)
            cap.release()
            cv2.destroyAllWindows()
            sys.exit()

# Function to track and update the high score
def track_high_score(score):
    try:
        with open("high_score.txt", "r") as file:
            high_score = int(file.read())
            if score > high_score:
                with open("high_score.txt", "w") as file:
                    file.write(str(score))
    except FileNotFoundError:
        with open("high_score.txt", "w") as file:
            file.write(str(score))

# Define possible directions for the pipes
directions = ['up', 'down']
next_pipe_direction = random.choice(directions)

# Main game loop
while True:
    # Variables to control the height and size of the opening
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Use face detection to get nose position
    results = face_detection.process(rgb_frame)
    if results.detections:
        for detection in results.detections:
            for id, lm in enumerate(detection.location_data.relative_keypoints):
                if id == 2:  # Nose tip
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    kuromi_x = cx
                    kuromi_y = cy

    # Check if it's time to create a new pipe
    if len(pipes) == 0 or pipes[-1][0] < width - 250:
        # Decide the height and size of the opening for the next pipe
        if next_pipe_direction == 'up':
            pipe_height = random.randint((height - gap - 100) // 20 * 20, (height - gap - 10) // 20 * 20)
        else:
            pipe_height = round(random.randint(1, 10) * 20)

        pipes.append([width, pipe_height])

        # Randomly select the direction of the opening for the next pipe
        next_pipe_direction = random.choice(directions)

    move_pipes()

    draw_pipes(frame)
    draw_kuromi(frame)

    # Check for collision with pipes
    for pipe in pipes:
        if pipe[0] < kuromi_x + 20 and pipe[0] + 50 > kuromi_x and (kuromi_y < pipe[1] or kuromi_y > pipe[1] + gap):
            pygame.mixer.Sound.play(game_over_sound)  # Play game over sound
            pipes = []
            score = 0
            cv2.destroyWindow("Flappy Kuromi uwu")
            game_over()

    track_high_score(score)

    with open("high_score.txt", "r") as file:
        high_score = int(file.read())
    cv2.putText(frame, f"High Score: {high_score}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (224, 217, 198), 2)

    cv2.putText(frame, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (222, 209, 235), 2)
    cv2.putText(frame, "Press 'p' to pause", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (201, 179, 201), 2)

    cv2.imshow("Flappy Kuromi uwu", frame)
    cv2.moveWindow('Flappy Kuromi uwu', pos_x, pos_y - 25)
    if cv2.waitKey(1) & 0xFF == ord('p'):
        pause()
