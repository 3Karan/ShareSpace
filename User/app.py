from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from pymongo import MongoClient
import secrets
from bson import ObjectId  # Import ObjectId from bson
import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a secure secret key

# MongoDB connection setup
client = MongoClient("mongodb+srv://kabiranavghan2454:12345@sharespacedb.giliwgs.mongodb.net/?retryWrites=true&w=majority&appName=ShareSpaceDb")
db = client.get_database('ShareSpaceDb')
users_collection = db.users
workspaces_collection = db['workspaces']
bookings_collection = db.bookings
payment_collection = db.payments  # Assuming a 'payments' collection exists for payment history


# Insert admin user if not already exists
admin_email = "admin@example.com"
admin_password = "adminpassword"

if not users_collection.find_one({"email": admin_email}):
    admin_user = {
        "username": "admin",
        "email": admin_email,
        "password": admin_password,
        "role": "admin"
    }
    users_collection.insert_one(admin_user)
    print(f"Admin user '{admin_email}' inserted into database.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if email is already registered
        if users_collection.find_one({'email': email}):
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('login'))

        # Add new user to the database
        new_user = {'username': username, 'email': email, 'password': password, 'role': 'user'}
        users_collection.insert_one(new_user)
        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if email and password match an admin user in the database
        admin_user = users_collection.find_one({'email': email, 'password': password, 'role': 'admin'})
        if admin_user:
            session['email'] = email

            flash.clear()  # Clear existing flash messages

            flash(f'Welcome, {email}!', 'success')
            return redirect(url_for('admin_dashboard'))

        # Check if email and password match a regular user in the database
        user = users_collection.find_one({'email': email, 'password': password, 'role': 'user'})
        if user:
            session['email'] = email
            flash(f'Welcome, {email}!', 'success')
            return redirect(url_for('user_dashboard'))

        flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('You have been logged out.', 'success')
    
    return redirect(url_for('login'))

@app.route('/user/dashboard')
def user_dashboard():
    if 'email' in session:
        email = session['email']
        user = users_collection.find_one({'email': email})
        if user:
            # Fetch workspaces including workspace_category from MongoDB
            workspaces = list(workspaces_collection.find())
            return render_template('user_dashboard.html', email=email, workspaces=workspaces)
        else:
            flash('User not found.', 'error')
            return redirect(url_for('login'))
    
    flash('Please log in to access the user dashboard.', 'error')
    return redirect(url_for('login'))



@app.route('/workspace/<int:workspace_id>')
def workspace_details(workspace_id):
    workspace = workspaces_collection.find_one({'id': workspace_id})
    if workspace:
        return render_template('workspace_details.html', workspace=workspace)
    flash('Workspace not found.', 'error')
    return redirect(url_for('user_dashboard'))

@app.route('/cart')
def cart():
    if 'cart' in session:
        cart_items = session['cart']
    else:
        cart_items = []

    total_price = sum(float(item.get('price_plan', 0)) * int(item.get('quantity', 0)) for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)




@app.route('/add_to_cart/<int:workspace_id>')
def add_to_cart(workspace_id):
    workspace = workspaces_collection.find_one({'workspace_id': workspace_id})
    
    if workspace:
        if 'cart' not in session:
            session['cart'] = []

        # Ensure to fetch and store the correct price information ('price' or 'price_plan')
        price = workspace.get('price', 0)  # Fetch 'price' from workspace document, default to 0 if not found
        price_plan = workspace.get('price_plan', '')  # Fetch 'price_plan' from workspace document, default to empty string if not found
        
        # Check if price or price_plan exists
        if price or price_plan:
            # Check if workspace is already in cart
            workspace_in_cart = next((item for item in session['cart'] if item['id'] == workspace_id), None)
            
            if workspace_in_cart:
                # Increase quantity if already in cart
                workspace_in_cart['quantity'] += 1
            else:
                # Add workspace to cart with quantity 1
                session['cart'].append({
                    'id': workspace_id,
                    'name': workspace['name'],
                    'price': price,  # Store 'price' or 'price_plan' in cart item
                    'price_plan': price_plan,  # Store 'price_plan' in cart item
                    'quantity': 1
                })
            
            flash(f'{workspace["name"]} added to cart.', 'success')
        else:
            flash('Price information missing for this workspace.', 'error')
    else:
        flash('Workspace not found.', 'error')
    
    return redirect(url_for('user_dashboard'))




@app.route('/remove_from_cart/<int:workspace_id>')
def remove_from_cart(workspace_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != workspace_id]
    return redirect(url_for('cart'))  # Redirecting to 'cart' endpoint after removing from cart

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'email' in session:
        email = session['email']
        user = users_collection.find_one({'email': email})
        if user:
            if request.method == 'POST':
                # Update user profile in MongoDB based on form submission
                username = request.form['username']
                full_name = request.form['full_name']
                phone_number = request.form['phone_number']

                # Example: Updating only phone_number here, adjust as per your needs
                users_collection.update_one({'email': email}, {'$set': {'phone_number': phone_number}})

                flash('Profile updated successfully.', 'success')
                return redirect(url_for('edit_profile'))

            # Render edit profile form with current user data
            return render_template('edit_profile.html', user=user)

    flash('Please log in to edit your profile.', 'error')
    return redirect(url_for('login'))

@app.route('/calendar')
def calendar():
    # Logic for calendar
    return render_template('calendar.html')

@app.route('/booking_status')
def booking_status():
    # Logic for booking status
    return render_template('booking_status.html')

@app.route('/usage_history')
def usage_history():
    # Logic for usage history
    return render_template('usage_history.html')

@app.route('/empty_cart', methods=['GET', 'POST'])
def empty_cart():
    if 'cart' in session:
        session.pop('cart')  # Clear the cart in session
    return redirect(url_for('user_dashboard'))  # Redirect to the cart page after clearing
@app.route('/payment_history')
def payment_history():
    # Dummy data for payment history
    payment_history_data = [
        {
            'id': '001',
            'workspace_name': 'Navghan',
            'amount': 1200,
            'date': '2024-06-01',
            'status': 'Paid'
        },
        {
            'id': '002',
            'workspace_name': 'Abhay',
            'amount': 1530,
            'date': '2024-06-10',
            'status': 'Pending'
        },
        {
            'id': '003',
            'workspace_name': 'Purva',
            'amount': 2200,
            'date': '2024-06-15',
            'status': 'Paid'
        }
    ]

    return render_template('payment_history.html', payments=payment_history_data)




@app.route('/view_payment_history')
def view_payment_history():
    if 'email' in session:
        email = session['email']
        user_payments = list(payment_collection.find({'user_email': email}))
        return render_template('payment_history.html', user_payments=user_payments)
    
    flash('Please log in to view payment history.', 'error')
    return redirect(url_for('login'))

@app.route('/checkout', methods=['GET'])
def checkout():
    # Fetch cart items and total price from session
    cart_items = session.get('cart', [])
    total_price = request.args.get('total_price', type=float)

    # Example payment options (replace with actual logic or data)
    payment_options = [
        {'id': 1, 'name': 'Credit/Debit Card', 'details': 'Add Card', 'icon': 'card'},
        {'id': 2, 'name': 'UPI', 'details': 'Add UPI ID', 'icon': 'upi'}
    ]

    return render_template('checkout.html', cart_items=cart_items, total_price=total_price, payment_options=payment_options)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    # Example: Logic to process the payment (not implemented here)
    # For demonstration, assume payment is successful

    # Remove item from cart and fetch necessary data
    workspace_id = session.pop('checkout_item_id', None)
    if workspace_id is None:
        flash('Error: Item not found in cart.', 'error')
        return redirect(url_for('cart'))

    # Example: Save payment details to MongoDB
    if 'email' in session:
        email = session['email']
        amount = request.form['amount']  # Adjust as per your payment form data
        timestamp = datetime.utcnow()

        # Insert payment details into 'payments' collection
        payment_details = {
            'user_email': email,
            'workspace_id': workspace_id,
            'amount': amount,
            'timestamp': timestamp
        }
        try:
            payment_collection.insert_one(payment_details)
            flash('Payment details recorded successfully.', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

        # Update workspace availability status to 'not_available'
        result = workspaces_collection.update_one({'workspace_id': workspace_id}, {'$set': {'availability_status': 'not_available'}})
        if result.modified_count == 1:
            flash('Workspace availability updated successfully.', 'info')
        else:
            flash('Failed to update workspace availability.', 'error')

        # Redirect to payment history after processing payment
        return redirect(url_for('payment_history'))

    flash('Please log in to process payment.', 'error')
    return redirect(url_for('login'))

@app.route('/update_workspace/<workspace_id>', methods=['PUT'])
def update_workspace(workspace_id):
    # Extract data from request
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    location = data.get('location')
    price_plan = data.get('price_plan')
    images = data.get('images')
    availability_status = data.get('availability_status')
    maintenance_status = data.get('maintenance_status')
    workspace_category = data.get('workspace_category')

    # Construct update query
    update_query = {
        '$set': {
            'name': name,
            'description': description,
            'location': location,
            'price_plan': price_plan,
            'images': images,
            'availability_status': availability_status,
            'maintenance_status': maintenance_status,
            'workspace_category': workspace_category
        }
    }

    # Update workspace in MongoDB
    result = workspaces_collection.update_one({'id': workspace_id}, update_query)

    if result.modified_count > 0:
        return jsonify({'message': 'Workspace updated successfully'}), 200
    else:
        return jsonify({'error': 'Failed to update workspace'}), 400


if __name__ == '__main__':
    app.run(debug=True)
