# import pytesseract
# from PIL import Image

# # Path to tesseract executable
# # Only necessary if Tesseract is not in your PATH
# # pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'

# # Open an image using Pillow
# image = Image.open("large-receipt-image-dataset-SRD/1004-receipt.jpg")

# # Use pytesseract to do OCR on the image
# text = pytesseract.image_to_string(image)

# print(text)


from google.cloud import vision
import io
import re
import os

def detect_text(path):
    """Detects text in the file."""

    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    
    texts = response.text_annotations
    text_coordinates = []
    for text in texts:
        text_content = text.description
        vertices = [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
        text_coordinates.append({"text": text_content, "coordinates": vertices})

    # Print or process the extracted text and coordinates
    for item in text_coordinates:
        print('bir sikim yapmiyor')
        print("Text:", item["text"])
        print("Coordinates:", item["coordinates"])
        print()
    # print(texts)/
    # print('Texts:')
    
    # for text in texts:

    #     # print('\n"{}"'.format(text.description))
    # if response.error.message:
    #     raise Exception('{}\nFor more info on error messages, check: https://cloud.google.com/apis/design/errors'.format(response.error.message))

    return str(texts[0].description)
# detect_text("/Users/mustafagumustas/Desktop/sinav/yildiz_evrimi_1.png")
def extract_items_prices(ocr_text):
    # Updated pattern to match the new format: Item name followed by qty and price
    # This pattern assumes the item names do not contain digits and are followed by
    # '1', the quantity, which is a reasonable assumption given the example.
    # It then captures the unit price which is the second number following the item name.
    pattern = re.compile(r'([a-zA-Z\s]+)\n1\n(\d+\.\d{2})')
    
    items_prices = re.findall(pattern, ocr_text)
    
    extracted_data = []
    for item, price in items_prices:
        # Cleaning item names by stripping trailing whitespaces
        clean_item = " ".join(item.strip().split())
        extracted_data.append({clean_item : price})

    return extracted_data

# if __name__ == '__main__':
#     # Path to the folder containing the images
#     folder_path = '/Users/mustafagumustas/Desktop/sinav'

#     # Iterate over all files in the folder
#     for filename in os.listdir(folder_path):
#         if filename.endswith('.jpg'):
#             file_path = os.path.join(folder_path, filename)
#             expo = detect_text(file_path)
            
#             # Create a new text file for each image and save the expo in them
#             path = "/Users/mustafagumustas/Desktop/sinav/text/"
#             file_name = filename.split('.')[0]  # Extract the image file name without extension
#             text_file_name = f"{path+file_name}.txt"  # Create the text file name by appending '.txt' to the image file name
#             with open(text_file_name, 'w') as file:
#                 file.write(expo)

    # print(extract_items_prices(expo))

import re

def extract_items_prices(receipt_text):
    # Normalize text
    text = receipt_text.lower()
    
    # Regular expression to find lines that may contain items and prices
    item_price_pattern = re.compile(r'^.*\d+\.\d{2}$', re.MULTILINE)
    
    # Filter lines that match the pattern and are likely to be items with prices
    potential_items = [line for line in text.split('\n') if item_price_pattern.match(line)]
    
    # Apply heuristic rules to further filter out non-item lines
    filtered_items = []
    for line in potential_items:
        if "subtotal" in line or "tax" in line or "total" in line or "cashier" in line:
            continue  # Skip known non-item lines
        filtered_items.append(line)
    
    return filtered_items


def extract_items(ocr_text):
    # Define a regex pattern for items and prices
    # The pattern assumes that items start with a digit (quantity) followed by text (item name) and a price on the next line
    pattern = re.compile(r'^(\d+) ([\w\s\#\'-]+)\n(\d+\.\d{2})', re.MULTILINE)

    # Find all matches of the pattern in the OCR text
    matches = pattern.findall(ocr_text)

    # Extract item names and prices
    items = [{match[1]: float(match[2])} for match in matches]

    return items

def read_txt_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content

def extract_receipt_data_corrected(ocr_text):
    # Split the OCR text into lines for processing
    lines = ocr_text.split('\n')

    # Initialize an empty dictionary for items
    items = {}

    # Regular expression to find prices
    price_pattern = re.compile(r'^(\d+\.\d{2})$')
    # Regular expression to find dates
    date_pattern = re.compile(r'(\w{3}\d{2}\s\d{2}:\d{2}(AM|PM))')

    # Temporary variables to hold the current item and price
    current_item = ''
    current_price = 0.0

    # Flags
    found_item = False

    for line in lines:
        line = line.strip()  # Remove whitespace
        if price_pattern.match(line):
            # If the line is a price, set the current price and the flag
            current_price = float(line)
            found_item = True
        elif found_item:
            # If we found a price on the last iteration, this line should be the item
            current_item = line
            items[current_item] = current_price
            # Reset the flag
            found_item = False

    # Extract date and total paid
    dates = date_pattern.findall(ocr_text)
    date = dates[0] if dates else 'Date not found'
    total_paid_pattern = re.compile(r'Total Paid\s+(\d+\.\d{2})')
    total_paid_match = total_paid_pattern.search(ocr_text)
    total_paid = float(total_paid_match.group(1)) if total_paid_match else 'Total not found'

    return {
        'date': date,
        'total_paid': total_paid,
        'items': items
    }
# Example usage
file_path = '/Users/mustafagumustas/financial_assistant/large-receipt-image-dataset-SRD/text/1180-receipt.txt'
# text = read_txt_file(file_path)

# # Example usage with one of the receipt texts
# receipt_text = """Katana Sushi
# 2818 Hewitt Ave
# Everett, WA 98201
# 425-512-9361
# ********
# Server: Michael C
# 05/11/18 8:47 PM
# Check #93
# Table D2
# Hamachi Collar
# $12.00
# Mega Poke Bowl
# $17.00
# Hamachi -
# Sashimi
# $12.00
# Maguro
# -
# - Sashimi
# $11.00
# Salmon - Sashimi
# $10.00
# 3 Sockeye Salmon - Sashimi
# $36.00
# Hamachi Japapeno
# $12.00
# Salmon Collar
# $10.00
# Escolar - Sashimi
# $11.00
# Subtotal
# $131.00
# Tax
# $12.71
# Total
# $143.71
# ***
# 153.71
# Thank You for your visit."""  # Insert the content of one of the receipt files here
# items = extract_items_prices(receipt_text)
# for i in extract_items(text):
#     print(i)

# print(extract_receipt_data_corrected(text))


from google.cloud import vision
from google.cloud.vision_v1 import types
from PIL import Image, ImageDraw

# Function to detect text and retrieve bounding boxes
def detect_text(image_path):
    client = vision.ImageAnnotatorClient()

    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    # Extract bounding box positions
    boxes = []
    for text in texts[1:]:  # Exclude the first element which contains the entire image text
        vertices = [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
        boxes.append(vertices)

    return boxes

# Function to visualize labeled text on the image
def visualize_text(image_path, boxes):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    for box in boxes:
        draw.polygon(box, outline='red')

    image.show()

# Example usage
    
    
image_path = "large-receipt-image-dataset-SRD/1183-receipt.jpg"
text_boxes = detect_text(image_path)
print(text_boxes)
visualize_text(image_path, text_boxes)

