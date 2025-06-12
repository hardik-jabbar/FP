import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
import stripe
import json

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Setup Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
# Set this to your domain
YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    orders = db.relationship('Order', backref='customer', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade="all, delete-orphan")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    inventory = db.Column(db.Integer, default=100)
    is_featured = db.Column(db.Boolean, default=False)
    is_new = db.Column(db.Boolean, default=False)
    is_sale = db.Column(db.Boolean, default=False)
    sale_price = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship('Product')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    total = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")
    stripe_payment_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product')
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Serve HTML files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_pages(path):
    if os.path.exists(path):
        return send_from_directory('.', path)
    return send_from_directory('.', 'index.html')

# API routes
@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    if category:
        products = Product.query.filter_by(category=category).all()
    else:
        products = Product.query.all()
    
    return jsonify([{
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'image_url': product.image_url,
        'category': product.category,
        'is_featured': product.is_featured,
        'is_new': product.is_new,
        'is_sale': product.is_sale,
        'sale_price': product.sale_price
    } for product in products])

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'image_url': product.image_url,
        'category': product.category,
        'is_featured': product.is_featured,
        'is_new': product.is_new,
        'is_sale': product.is_sale,
        'sale_price': product.sale_price
    })

# Authentication routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'Email already in use'}), 400
    
    # Hash the password
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    # Create new user
    user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_password
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Account created successfully!'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and bcrypt.check_password_hash(user.password, data['password']):
        login_user(user)
        return jsonify({'success': True, 'user': {'id': user.id, 'name': user.name, 'email': user.email}})
    
    return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True})

@app.route('/api/user', methods=['GET'])
@login_required
def get_user():
    return jsonify({
        'id': current_user.id,
        'name': current_user.name,
        'email': current_user.email
    })

# Cart routes
@app.route('/api/cart', methods=['GET'])
@login_required
def get_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    items = []
    total = 0
    
    for item in cart_items:
        product = item.product
        price = product.sale_price if product.is_sale and product.sale_price else product.price
        item_total = price * item.quantity
        total += item_total
        
        items.append({
            'id': item.id,
            'product_id': product.id,
            'name': product.name,
            'price': price,
            'quantity': item.quantity,
            'image_url': product.image_url,
            'subtotal': item_total
        })
    
    return jsonify({
        'items': items,
        'total': total
    })

@app.route('/api/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    product = Product.query.get_or_404(product_id)
    
    # Check if item already in cart
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Item added to cart'})

@app.route('/api/cart/update', methods=['POST'])
@login_required
def update_cart():
    data = request.get_json()
    cart_item_id = data.get('cart_item_id')
    quantity = data.get('quantity')
    
    cart_item = CartItem.query.filter_by(id=cart_item_id, user_id=current_user.id).first_or_404()
    
    if quantity > 0:
        cart_item.quantity = quantity
    else:
        db.session.delete(cart_item)
    
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/cart/remove', methods=['POST'])
@login_required
def remove_from_cart():
    data = request.get_json()
    cart_item_id = data.get('cart_item_id')
    
    cart_item = CartItem.query.filter_by(id=cart_item_id, user_id=current_user.id).first_or_404()
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({'success': True})

# Stripe checkout route
@app.route('/api/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    data = request.get_json()
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    line_items = []
    
    for item in cart_items:
        product = item.product
        price = product.sale_price if product.is_sale and product.sale_price else product.price
        
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': product.name,
                    'images': [product.image_url],
                },
                'unit_amount': int(price * 100),  # Stripe expects amount in cents
            },
            'quantity': item.quantity,
        })
    
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f'https://{YOUR_DOMAIN}/order-success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'https://{YOUR_DOMAIN}/cart',
        )
        
        return jsonify({'id': checkout_session.id})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/order-success', methods=['GET'])
@login_required
def order_success():
    session_id = request.args.get('session_id')
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Create order from cart
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        
        if not cart_items:
            return jsonify({'error': 'Cart is empty'}), 400
            
        # Calculate total
        total = 0
        for cart_item in cart_items:
            product = cart_item.product
            price = product.sale_price if product.is_sale and product.sale_price else product.price
            total += price * cart_item.quantity
        
        # Create order
        order = Order(
            user_id=current_user.id,
            status='paid',
            total=total,
            shipping_address=session.shipping.address.line1 if session.shipping else 'Default Address',
            stripe_payment_id=session_id
        )
        
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Create order items
        for cart_item in cart_items:
            product = cart_item.product
            price = product.sale_price if product.is_sale and product.sale_price else product.price
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=cart_item.quantity,
                price=price
            )
            
            db.session.add(order_item)
        
        # Clear the cart
        for cart_item in cart_items:
            db.session.delete(cart_item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'order_id': order.id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Order routes
@app.route('/api/orders', methods=['GET'])
@login_required
def get_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    
    return jsonify([{
        'id': order.id,
        'status': order.status,
        'total': order.total,
        'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'items_count': len(order.order_items)
    } for order in orders])

@app.route('/api/orders/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    items = [{
        'id': item.id,
        'product_id': item.product_id,
        'name': item.product.name,
        'price': item.price,
        'quantity': item.quantity,
        'subtotal': item.price * item.quantity,
        'image_url': item.product.image_url
    } for item in order.order_items]
    
    return jsonify({
        'id': order.id,
        'status': order.status,
        'total': order.total,
        'shipping_address': order.shipping_address,
        'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'items': items
    })

# Admin API routes (would need more security in production)
@app.route('/api/admin/products', methods=['POST'])
@login_required
def create_product():
    # In production, add admin role check
    data = request.get_json()
    
    product = Product(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        image_url=data['image_url'],
        category=data['category'],
        inventory=data.get('inventory', 100),
        is_featured=data.get('is_featured', False),
        is_new=data.get('is_new', False),
        is_sale=data.get('is_sale', False),
        sale_price=data.get('sale_price')
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'id': product.id
    })

@app.route('/api/admin/products/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    # In production, add admin role check
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.image_url = data.get('image_url', product.image_url)
    product.category = data.get('category', product.category)
    product.inventory = data.get('inventory', product.inventory)
    product.is_featured = data.get('is_featured', product.is_featured)
    product.is_new = data.get('is_new', product.is_new)
    product.is_sale = data.get('is_sale', product.is_sale)
    product.sale_price = data.get('sale_price', product.sale_price)
    
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/admin/products/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    # In production, add admin role check
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({'success': True})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized'}), 401

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)