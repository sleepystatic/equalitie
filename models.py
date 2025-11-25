from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    images = db.Column(db.Text)  # JSON array of image filenames
    sizes = db.Column(db.Text)  # JSON array of available sizes
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, category, price, description, images, sizes, stock):
        self.name = name
        self.category = category
        self.price = price
        self.description = description
        self.images = json.dumps(images)
        self.sizes = json.dumps(sizes)
        self.stock = stock

    def get_images(self):
        return json.loads(self.images) if self.images else []

    def get_sizes(self):
        return json.loads(self.sizes) if self.sizes else []

    def get_main_image(self):
        images = self.get_images()
        return images[0] if images else 'placeholder.jpg'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'sale_price': round(self.price * 0.40, 2),
            'description': self.description,
            'images': self.get_images(),
            'sizes': self.get_sizes(),
            'stock': self.stock
        }


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    size = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref='cart_items')

    def to_dict(self):
        return {
            'id': self.id,
            'product': self.product.to_dict(),
            'size': self.size,
            'quantity': self.quantity
        }


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)

    # Shipping information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(50), default='United States')

    # Order details
    items = db.Column(db.Text)  # JSON array of order items
    subtotal = db.Column(db.Float, nullable=False)
    shipping = db.Column(db.Float, default=0.00)
    total = db.Column(db.Float, nullable=False)

    # Payment
    stripe_payment_intent = db.Column(db.String(100))
    payment_status = db.Column(db.String(20), default='pending')

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, order_number, email, first_name, last_name, address, city, state, zip_code, items, subtotal,
                 total):
        self.order_number = order_number
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.items = json.dumps(items)
        self.subtotal = subtotal
        self.total = total

    def get_items(self):
        return json.loads(self.items) if self.items else []