import pytesseract
from PIL import Image
import re
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_receipt(file):
    try:
        # Save the uploaded file temporarily
        temp_path = "temp_receipt.png"
        file.save(temp_path)
        logging.info(f"Saved temporary file: {temp_path}")

        # Use Tesseract OCR to extract text from the image
        text = pytesseract.image_to_string(Image.open(temp_path))
        logging.info("Successfully extracted text from image")

        # Process the extracted text
        lines = text.split('\n')
        
        # Extract store name (assuming it's the first line)
        store_name = lines[0].strip()
        logging.info(f"Extracted store name: {store_name}")

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
                logging.info(f"Extracted item: {item_name}, Price: {price}, Category: {category}")

        # Determine overall category
        category = determine_overall_category(items)
        logging.info(f"Determined overall category: {category}")

        # Clean up temporary file
        os.remove(temp_path)
        logging.info(f"Removed temporary file: {temp_path}")

        return {
            'store_name': store_name,
            'items': items,
            'total_amount': total_amount,
            'category': category
        }
    except Exception as e:
        logging.error(f"Error processing receipt: {str(e)}")
        raise

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
    return max(category_counts, key=category_counts.get)
