import argparse
import os
import PyPDF2
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import re
import cv2
import numpy as np
from scipy import stats


known_account_numbers = ['1234567890123456', '0987654321098765']
transaction_limit = 1000.00
#Step 1: Taking the file path as an argument
parser = argparse.ArgumentParser(description='Process an image or PDF document.')
parser.add_argument('FilePath', metavar='filepath', type=str, help='the path to the document')
args = parser.parse_args()
print(f"Processing file at {args.FilePath}")

#Step 2: Extracting the metadata
def extract_pdf_metadata(file_path):
    with open(file_path, 'rb') as file:
        pdf = PyPDF2.PdfReader(file)
        metadata = pdf.metadata
        return metadata
    

def extract_image_metadata(file_path):
    with Image.open(file_path) as img:
        metadata = img._getexif()
        return metadata
    
#Step 3: Analyzing the metadata
def analyze_pdf_metadata(metadata):
    creation_date = metadata.get('/CreationDate', '')
    mod_date = metadata.get('/ModDate', '')

    if creation_date != mod_date:
        print("The document may have been edited after creation.")
    else:
        print("The document has not been edited after creation.")

def analyze_image_metadata(metadata):
    software = metadata.get(305, '')

    if 'photoshop' in software.lower():
        print("The image may have been edited in Photoshop.")
    else:
        print("The image does not appear to have been edited in Photoshop.")




#Step 4: Extracting text from the document
def extract_text_from_image(file_path):
    with Image.open(file_path) as img:
        text = pytesseract.image_to_string(img)
        return text
    


def extract_text_from_pdf(file_path):
    pages = convert_from_path(file_path)
    text = ''
    for page in pages:
        text += pytesseract.image_to_string(page)
    return text


#Step 5: Analyzing the text
def analyze_text(text, known_account_numbers, transaction_limit):
    account_number_pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
    date_pattern = r'\b\d{4}[-/]\d{2}[-/]\d{2}\b'
    transaction_amount_pattern = r'\b\d+\.\d{2}\b'

    account_number_match = re.search(account_number_pattern, text)
    date_match = re.search(date_pattern, text)
    transaction_amount_match = re.search(transaction_amount_pattern, text)

    if account_number_match:
        account_number = account_number_match.group().replace(' ', '').replace('-', '')
        if account_number in known_account_numbers:
            print(f"Found a known account number: {account_number}")
        else:
            print(f"Found an unknown account number: {account_number}")
            print("Document may be Edited.")
    else:
        print("Did not find an account number.")
        print("Document may be Edited.")

    if date_match:
        print(f"Found a date: {date_match.group()}")
    else:
        print("Did not find a date.")
        print("Document may be Edited.")

    if transaction_amount_match:
        transaction_amount = float(transaction_amount_match.group())
        if transaction_amount > transaction_limit:
            print(f"Found a large transaction amount: {transaction_amount}")
        else:
            print(f"Found a transaction amount: {transaction_amount}")
            print("Document may be Edited.")
    else:
        print("Did not find a transaction amount.")
        print("Document may be Edited.")



#step 6: Calculating the image quality score
def calculate_image_quality_score(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurriness = cv2.Laplacian(gray, cv2.CV_64F).var()
    median = np.median(gray)
    noise = stats.median_abs_deviation(gray - median)
    contrast = gray.std()
    brightness = gray.mean()
    score = blurriness - noise + contrast + brightness
    return score

def is_tampered(image_path, threshold):
    score = calculate_image_quality_score(image_path)
    if score < threshold:
        print("Image is tampered.")
    else:
        print("Image is not tampered.")
    

file_extension = os.path.splitext(args.FilePath)[1].lower()
if file_extension == '.pdf':
    metadata = extract_pdf_metadata(args.FilePath)
    print("Metadata:", metadata)
    analyze_pdf_metadata(metadata)
    text = extract_text_from_pdf(args.FilePath)
    analyze_text(text, known_account_numbers, transaction_limit)
    # is_tampered(args.FilePath, 100)
elif file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
    metadata = extract_image_metadata(args.FilePath)
    print("Metadata:", metadata)
    analyze_image_metadata(metadata)
    text = extract_text_from_image(args.FilePath)
    analyze_text(text, known_account_numbers, transaction_limit)
    is_tampered(args.FilePath, 100)
else:
    print("Unsupported file format.")
    metadata = None







