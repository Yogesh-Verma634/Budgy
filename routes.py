import os
from flask import render_template, request, jsonify, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, Receipt, Item
from receipt_processor import process_receipt

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.form
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(user)
    db.session.commit()
    flash('Registration successful. Please log in.', 'success')
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    data = request.form
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        flash('Logged in successfully.', 'success')
        return redirect(url_for('dashboard'))
    flash('Invalid username or password.', 'error')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    # In a real application, you'd check if the user is logged in here
    return render_template('dashboard.html')

@app.route('/upload_receipt', methods=['POST'])
def upload_receipt():
    if 'receipt' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['receipt']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        # Process the receipt
        receipt_data = process_receipt(file)
        # Save the receipt data to the database
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

@app.route('/get_expenses')
def get_expenses():
    # In a real application, you'd filter by the logged-in user
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
