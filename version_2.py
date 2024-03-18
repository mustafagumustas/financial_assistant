from google.cloud import vision
import io
from google.cloud.vision_v1 import types
from PIL import Image, ImageDraw
import os
import json
# Instantiate a client
client = vision.ImageAnnotatorClient()

def visualize_text(image_path, boxes):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    for box in boxes:
        draw.polygon(box, outline='red')

    image.show()

def get_file_paths(path):
    file_paths = []
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            file_paths.append(os.path.join(path, file))
    return file_paths

# Read the image file
def detect_text(image_path):
    if image_path.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        print(image_path)
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()

        # Construct an image instance
        image = vision.Image(content=content)

        # Perform text detection
        response = client.text_detection(image=image)

        # Extract text annotations
        texts = response.text_annotations

        # Construct JSON-like data
        data = []
        for text in texts:
            entry = {'description': text.description.strip()}
            vertices = [{'x': vertex.x, 'y': vertex.y} for vertex in text.bounding_poly.vertices]
            entry['bounding_poly'] = {'vertices': vertices}
            data.append(entry)

        # Save the JSON-like data to a text file
        save_path = '/Users/mustafagumustas/financial_assistant/json/'
        file_name = image_path.split('.')[0]  # Extract the image file name without extension
        text_file_name = f"{save_path+file_name.split('/')[-1]}.json"  # Create the text file name by appending '.txt' to the image file name

        with open(text_file_name, 'w') as file:
            json.dump(data, file, indent=2)

    else:
        print(f"{image_path} is not a valid image file.")
            


# Example usage
path = "/Users/mustafagumustas/financial_assistant/large-receipt-image-dataset-SRD"
file_paths = get_file_paths(path)
for i in file_paths:
    detect_text(i)
    print("\n")


