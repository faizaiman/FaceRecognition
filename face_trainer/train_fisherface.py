import cv2
import os
from imutils import paths
import numpy as np
import requests

def upload():
    print("UPLOAD FILE")
    url = 'http://raspberrypi.local:5000/upload'
    filepath = 'fisherface_trained_model.yml'
    with open(filepath, 'rb') as f:
        requests.post(url, data=f)
    print("OK 200 : Done Upload Fisher")

def train():
    print("[INFO] start processing faces...")
    imagePaths = list(paths.list_images("./face_trainer/dataset"))

    # Initialize lists for face samples and corresponding IDs
    faceSamples = []
    faceIDs = []

    # Standard size for all faces
    standard_size = (200, 200)

    # Loop over each image path
    for imagePath in imagePaths:
        # Read and convert the image to grayscale
        image = cv2.imread(imagePath)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Resize the image to the standard size
        gray = cv2.resize(gray, standard_size)

        # Extract the face ID from the directory name
        faceID = os.path.basename(os.path.dirname(imagePath))

        # Check if faceID is a number and convert it to int
        if faceID.isdigit():
            faceID = int(faceID)
        else:
            continue  # Skip this file if faceID is not a number

        # Append the face and ID to the lists
        faceSamples.append(gray)
        faceIDs.append(faceID)

    # Create and train the FisherFace recognizer
    recognizer = cv2.face.FisherFaceRecognizer_create()
    recognizer.train(faceSamples, np.array(faceIDs))

    # Save the trained model
    recognizer.write("fisherface_trained_model.yml")
    print("[INFO] Model trained and saved.")

    upload()

if __name__ == "__main__":
    train()
