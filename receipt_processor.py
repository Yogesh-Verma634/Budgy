import pytesseract
from PIL import Image
import re

def process_receipt(file):
    # Save the uploaded file temporarily
    temp_path = "temp_receipt.png"
    file.save(temp_path)

    # Use Tesseract OCR to extract text from the image
    text = pytesseract.image_to_string(Image.open(temp_path))

    # Process the extracted text
    lines = text.split('\n')
    
    # Extract store name (assuming it's the first line)
    store_name = lines[0].strip()

    # Extract items and prices
    items = []
    total_amount = 0
    for line in lines[1:]:
        match = re.search(r'(.+)\s+(\d+\.\d{2})', line)
        if match:
            item_name = match.group(1).strip()
            price = float(match.group(2))
            items.append({'name': item_name, 'price': price, 'category': categorize_item(item_name)})
            total_amount += price

    # Determine overall category (simplified)
    category = 'Groceries' if any('food' in item['name'].lower() for item in items) else 'Clothing'

    return {
        'store_name': store_name,
        'items': items,
        'total_amount': total_amount,
        'category': category
    }

def categorize_item(item_name):
    # Simplified categorization logic
    if any(word in item_name.lower() for word in ['fruit', 'vegetable', 'meat', 'dairy']):
        return 'Groceries'
    elif any(word in item_name.lower() for word in ['shirt', 'pants', 'dress', 'shoe']):
        return 'Clothing'
    else:
        return 'Other'
