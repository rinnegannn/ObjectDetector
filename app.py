import cv2
from tkinter import Tk, filedialog
import pyttsx3
from ultralytics import YOLO  # Import YOLOv8 from Ultralytics
from flask import Flask, request, render_template

app = Flask(__name__)

def upload_image():
    # Open file dialog to upload an image
    root = Tk()
    root.withdraw()  # Hide the Tkinter root window
    file_path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image files", "*.jpg;*.png;*.jpeg")])
    return file_path

def detect_objects(image_path):
    # Initialize text-to-speech engine
    engine = pyttsx3.init()

    # Load the YOLOv8 model (using the largest and most accurate YOLOv8 model, 'yolov8x.pt')
    model = YOLO("yolov8x.pt")  

    # Load the image
    img = cv2.imread(image_path)

    # Perform inference on the image
    results = model(img)

    # Extract detection results
    detections = results[0].boxes.data.cpu().numpy()  # Get detection results as a numpy array
    names = results[0].names  # Get class names

    # Print all detections for debugging
    print("All Detections:")
    print(detections)

    # Filter results based on confidence score (> 0.1)
    filtered_detections = [det for det in detections if det[4] > 0.3]  # det[4] is the confidence score

    # If no detections, print a message and return
    if not filtered_detections:
        engine.say(f"No objects detected in the image")
        engine.runAndWait()
        return

    # Calculate scaling factors based on image size
    height, width = img.shape[:2]
    scale_factor = max(height, width) / 1000  # Adjust 1000 to control the scaling sensitivity

    # Define parameters for the label display
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.5 * scale_factor  # Scale font size based on image size
    font_thickness = int(3 * scale_factor)  # Scale font thickness based on image size
    text_color = (255, 255, 255)  # White text
    background_color = (0, 0, 0)  # Black background
    padding = int(20 * scale_factor)  # Padding around text
    line_spacing = int(10 * scale_factor)  # Space between lines

    # Calculate the starting position for the labels at the bottom
    label_height = int(font_scale * 50)  # Approximate height of one line of text
    start_y = img.shape[0] - padding - label_height  # Start from the bottom

    # Draw bounding boxes on the original image
    for detection in filtered_detections:
        x1, y1, x2, y2, conf, cls_id = detection
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        label = names[int(cls_id)]  # Get the class name
        color = (0, 255, 0)  # Green color for bounding boxes
        box_thickness = int(4 * scale_factor)  # Scale bounding box thickness
        cv2.rectangle(img, (x1, y1), (x2, y2), color, box_thickness)

    # Draw labels at the bottom of the image
    for detection in filtered_detections:
        x1, y1, x2, y2, conf, cls_id = detection
        label = names[int(cls_id)]  # Get the class name

        # Calculate text size
        (text_width, text_height), _ = cv2.getTextSize(label, font, font_scale, font_thickness)

        # Draw background rectangle for the label
        cv2.rectangle(img, (padding, start_y - text_height), (padding + text_width, start_y), background_color, -1)

        # Draw the label text
        cv2.putText(img, label, (padding, start_y), font, font_scale, text_color, font_thickness)

        # Move the starting position up for the next label
        start_y -= (text_height + line_spacing)

    # Resize the image for display to fit on the screen (e.g., 800px width)
    screen_width = 800
    aspect_ratio = float(img.shape[1]) / float(img.shape[0])
    new_width = screen_width
    new_height = int(screen_width / aspect_ratio)
    img_resized = cv2.resize(img, (new_width, new_height))

    # Display the output image with labels in BGR (no need for color conversion)
    cv2.imshow("Detected Objects", img_resized)
    cv2.waitKey(100)  # Wait for 100ms to ensure the window is open

    # Initialize text-to-speech engine
    engine = pyttsx3.init()

    # Read the labels aloud (only the name of the item)
    for detection in filtered_detections:
        label = names[int(detection[5])]  # Get the class name
        engine.say(f"I see a {label}")

    # Run the text-to-speech engine
    engine.runAndWait()

    # Wait for a key press to close the image window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Upload an image
    image_path = upload_image()
    if image_path:
        detect_objects(image_path)
    else:
        print("No image selected!")