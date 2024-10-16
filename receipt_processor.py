import pytesseract
from PIL import Image
import re
import logging
import io

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def process_receipt(file):
    try:
        logging.debug(f"Starting to process receipt: {file.filename}")
        
        # Read the file content
        file_content = file.read()
        logging.debug(f"File content read, size: {len(file_content)} bytes")
        
        # Open the image using PIL
        with Image.open(io.BytesIO(file_content)) as img:
            logging.debug(f"Image opened. Mode: {img.mode}, Size: {img.size}, Format: {img.format}")
            
            # Convert image to RGB mode if it's not already
            if img.mode != 'RGB':
                logging.debug(f"Converting image from {img.mode} to RGB")
                img = img.convert('RGB')
            
            # Use Tesseract OCR to extract text from the image
            logging.debug("Starting OCR text extraction")
            text = pytesseract.image_to_string(img)
            logging.debug(f"OCR extraction completed. Extracted text length: {len(text)}")
        
        # Process the extracted text
        lines = text.split('\n')
        logging.debug(f"Text split into {len(lines)} lines")
        
        # Extract store name (assuming it's the first line)
        store_name = lines[0].strip()
        logging.debug(f"Extracted store name: {store_name}")

        # Extract items and prices
        items = []
        total_amount = 0
        for line in lines[1:]:
            match = re.search(r'(.+)\s+(\d+\.\d{2})', line)
            if match:
                item_name = match.group(1).strip()
                price = float(match.group(2))
                category = categorize_item(item_name)
                items.append({'name': item_name, 'price': price, 'category': category})
                total_amount += price
                logging.debug(f"Extracted item: {item_name}, Price: {price}, Category: {category}")

        # Determine overall category
        category = determine_overall_category(items)
        logging.debug(f"Determined overall category: {category}")

        logging.info(f"Receipt processing completed successfully. Items: {len(items)}, Total: {total_amount}")
        return {
            'store_name': store_name,
            'items': items,
            'total_amount': total_amount,
            'category': category
        }
    except IOError as e:
        logging.error(f"Error opening or processing the image: {str(e)}")
        raise ValueError(f"Unable to open or process the image. Error: {str(e)}")
    except pytesseract.TesseractError as e:
        logging.error(f"Tesseract OCR error: {str(e)}")
        raise ValueError(f"Error in text recognition. Tesseract error: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error processing receipt: {str(e)}")
        raise ValueError(f"An unexpected error occurred while processing the receipt: {str(e)}")

def categorize_item(item_name):
    # Improved categorization logic
    categories = {
        'Groceries': ['fruit', 'vegetable', 'meat', 'dairy', 'bread', 'cereal', 'snack'],
        'Clothing': ['shirt', 'pants', 'dress', 'shoe', 'jacket', 'socks'],
        'Electronics': ['phone', 'laptop', 'charger', 'cable', 'headphone'],
        'Home': ['furniture', 'decor', 'kitchen', 'bathroom', 'bedroom'],
        'Personal Care': ['soap', 'shampoo', 'toothpaste', 'cosmetics', 'lotion']
    }

    item_name_lower = item_name.lower()
    for category, keywords in categories.items():
        if any(keyword in item_name_lower for keyword in keywords):
            return category
    return 'Other'

def determine_overall_category(items):
    category_counts = {}
    for item in items:
        category_counts[item['category']] = category_counts.get(item['category'], 0) + 1
    return max(category_counts, key=category_counts.get) if category_counts else 'Unknown'
