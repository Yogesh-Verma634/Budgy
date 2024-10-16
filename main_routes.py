from flask import Blueprint, render_template, request, jsonify
from app import db
from models import Receipt, Item
from receipt_processor import process_receipt

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main.route('/upload_receipt', methods=['POST'])
def upload_receipt():
    if 'receipt' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['receipt']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        receipt_data = process_receipt(file)
        new_receipt = Receipt(
            user_id=1,  # Replace with actual user ID in a real application
            store_name=receipt_data['store_name'],
            total_amount=receipt_data['total_amount'],
            category=receipt_data['category']
        )
        db.session.add(new_receipt)
        db.session.commit()

        for item in receipt_data['items']:
            new_item = Item(
                receipt_id=new_receipt.id,
                name=item['name'],
                price=item['price'],
                category=item['category']
            )
            db.session.add(new_item)
        db.session.commit()

        return jsonify({'message': 'Receipt processed successfully'}), 200

@main.route('/get_expenses')
def get_expenses():
    receipts = Receipt.query.all()
    expenses = []
    for receipt in receipts:
        expense = {
            'store_name': receipt.store_name,
            'date': receipt.date.strftime('%Y-%m-%d'),
            'total_amount': receipt.total_amount,
            'category': receipt.category,
            'items': [{
                'name': item.name,
                'price': item.price,
                'category': item.category
            } for item in receipt.items]
        }
        expenses.append(expense)
    return jsonify(expenses)
