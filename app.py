import cv2
import pyttsx3
import os
import numpy as np
from ultralytics import YOLO
from flask import Flask, request, render_template, jsonify
import base64
from datetime import datetime  # Import datetime to generate unique filenames

app = Flask(__name__)

# Create upload directory when app starts
os.makedirs('static/uploads', exist_ok=True)

# Welcome page for the program
@app.route("/")
def welcome():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    print("Uploading image...")
   
    # Check if file is in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
   
    file = request.files['file']
   
    # Check if file name is empty
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
   
    # Read the file into a numpy array
    filestr = file.read()
    npimg = np.frombuffer(filestr, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
   
    # Process the image and get the result
    processed_img, detected_objects = detect_objects(img)
   
    # Save the processed image to the uploads folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Generate a unique timestamp
    filename = f"static/uploads/detected_image_{timestamp}.jpg"  # Create a unique filename
    cv2.imwrite(filename, processed_img)  # Save the image
   
    # Encode the processed image to base64 for sending back to client
    _, buffer = cv2.imencode('.jpg', processed_img)
    encoded_img = base64.b64encode(buffer).decode('utf-8')
   
    # Return the processed image and detected objects
    return jsonify({
        "image": encoded_img,
        "objects": detected_objects,
        "saved_path": filename  # Return the path where the image is saved
    })

@app.route("/read-aloud", methods=["POST"])
def read_aloud():
    data = request.json
    objects = data.get('objects', [])
   
    if not objects:
        return jsonify({"message": "No objects to read"}), 200
   
    # Initialize text-to-speech engine
    engine = pyttsx3.init()
   
    # Read objects aloud
    for obj in objects:
        engine.say(f"I see a {obj}")
   
    # Run the text-to-speech engine
    engine.runAndWait()
   
    return jsonify({"message": "Objects read aloud"}), 200

def detect_objects(img):
    # Load the YOLOv8 model
    model = YOLO("yolov8x.pt")  

    # Perform inference on the image
    results = model(img)

    # Extract detection results
    detections = results[0].boxes.data.cpu().numpy()
    names = results[0].names

    # Filter results based on confidence score
    filtered_detections = [det for det in detections if det[4] > 0.3]

    # List to store detected object names
    detected_objects = []

    # Calculate scaling factors based on image size
    height, width = img.shape[:2]
    scale_factor = max(height, width) / 1000

    # Define parameters for the label display
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.5 * scale_factor
    font_thickness = int(3 * scale_factor)
    text_color = (255, 255, 255)
    background_color = (0, 0, 0)
    padding = int(20 * scale_factor)
    line_spacing = int(10 * scale_factor)

    # Calculate the starting position for the labels at the bottom
    label_height = int(font_scale * 50)
    start_y = img.shape[0] - padding - label_height

    # Draw bounding boxes on the original image
    for detection in filtered_detections:
        x1, y1, x2, y2, conf, cls_id = detection
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        label = names[int(cls_id)]
        detected_objects.append(label)
        color = (0, 255, 0)
        box_thickness = int(4 * scale_factor)
        cv2.rectangle(img, (x1, y1), (x2, y2), color, box_thickness)

    # Draw labels at the bottom of the image
    for detection in filtered_detections:
        x1, y1, x2, y2, conf, cls_id = detection
        label = names[int(cls_id)]

        # Calculate text size
        (text_width, text_height), _ = cv2.getTextSize(label, font, font_scale, font_thickness)

        # Draw background rectangle for the label
        cv2.rectangle(img, (padding, start_y - text_height), (padding + text_width, start_y), background_color, -1)

        # Draw the label text
        cv2.putText(img, label, (padding, start_y), font, font_scale, text_color, font_thickness)

        # Move the starting position up for the next label
        start_y -= (text_height + line_spacing)

    return img, detected_objects

# Runs the program
if __name__ == "__main__":
    app.run(debug=True)