from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import db
from models import Receipt, Item
from receipt_processor import process_receipt
import logging
import mimetypes

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main.route('/upload_receipt', methods=['POST'])
@login_required
def upload_receipt():
    if 'receipt' not in request.files:
        current_app.logger.error('No file part in the request')
        return jsonify({'error': 'No file uploaded. Please select an image.'}), 400

    file = request.files['receipt']
    if file.filename == '':
        current_app.logger.error('No selected file')
        return jsonify({'error': 'No file selected. Please choose an image.'}), 400

    if file:
        # Check if the file is an allowed image type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        current_app.logger.debug(f"File extension: {file_extension}")
        
        if file_extension not in allowed_extensions:
            current_app.logger.error(f"Invalid file extension: {file_extension}")
            return jsonify({'error': 'Invalid file type. Please upload an image (PNG, JPG, JPEG, or GIF).'}), 400

        # Check the MIME type of the file
        mime_type = mimetypes.guess_type(file.filename)[0]
        current_app.logger.debug(f"MIME type: {mime_type}")
        
        if not mime_type or not mime_type.startswith('image/'):
            current_app.logger.error(f"Invalid MIME type: {mime_type}")
            return jsonify({'error': 'Invalid file type. Please upload a valid image file.'}), 400

        try:
            current_app.logger.info(f'Processing receipt: {file.filename}')
            receipt_data = process_receipt(file)
            current_app.logger.info(f'Receipt processed successfully: {receipt_data}')
            
            new_receipt = Receipt(
                user_id=current_user.id,
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

            return jsonify({'message': 'Receipt processed successfully', 'data': receipt_data}), 200
        except ValueError as e:
            current_app.logger.error(f'Error processing receipt: {str(e)}')
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            current_app.logger.error(f'Unexpected error processing receipt: {str(e)}')
            return jsonify({'error': 'An unexpected error occurred. Please try again or contact support.'}), 500

@main.route('/get_expenses')
@login_required
def get_expenses():
    receipts = Receipt.query.filter_by(user_id=current_user.id).all()
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
