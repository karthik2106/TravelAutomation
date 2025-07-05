from PIL import Image
import pytesseract

# Make sure your local Tesseract install path is set correctly
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

def get_prices_from_ocr(image_file_or_path):
    # This allows both uploaded file and file path
    if isinstance(image_file_or_path, str):
        img = Image.open(image_file_or_path)
    else:
        img = Image.open(image_file_or_path)

    text = pytesseract.image_to_string(img)

    basic_fare = None
    total_fare = None

    for line in text.splitlines():
        if "INR" in line and any(char.isdigit() for char in line):
            parts = line.split()
            try:
                inr_index = parts.index("INR")
                basic_fare = int(parts[inr_index + 1].replace(",", ""))
                total_fare = int(parts[inr_index + 3].replace(",", ""))
                break
            except (IndexError, ValueError):
                continue

    if basic_fare and total_fare:
        return basic_fare, total_fare, text
    else:
        raise ValueError("Could not find fares in image text.")