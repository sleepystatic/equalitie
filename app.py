from flask import Flask, session
from datetime import timedelta
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'production_fallback_only')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Stripe configuration - now from environment
app.config['STRIPE_PUBLIC_KEY'] = os.getenv('STRIPE_PUBLIC_KEY')
app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')

print(f"Stripe Public Key: {app.config['STRIPE_PUBLIC_KEY'][:10]}...")  # Shows first 10 chars


# Initialize database
from models import db

db.init_app(app)

# Register blueprints
from routes.main import main_bp
from routes.cart import cart_bp
from routes.checkout import checkout_bp

app.register_blueprint(main_bp)
app.register_blueprint(cart_bp, url_prefix='/cart')
app.register_blueprint(checkout_bp, url_prefix='/checkout')

# Create database tables
with app.app_context():
    db.create_all()

    # Add sample products if database is empty
    from models import Product

    if Product.query.count() == 0:
        sample_products = [
            # Shirts
            Product(
                name='Equali-Tee',
                category='shirts',
                price=50.00,
                description='',
                images=['shirt-1.jpg', 'shirt-1-alt.jpg'],
                sizes=['M', 'L', 'XL'],
                stock=50
            ),
            Product(
                name='Green/Beige Polo',
                category='shirts',
                price=50.00,
                description='',
                images=['shirt-2.jpg', 'shirt-2-alt.jpg'],
                sizes=['M', 'L', 'XL'],
                stock=50
            ),
            Product(
                name='Black/Green Polo',
                category='shirts',
                price=50.00,
                description='',
                images=['shirt-3.jpg', 'shirt-3-alt.jpg'],
                sizes=['M', 'L', 'XL'],
                stock=50
            ),
            Product(
                name='Black/Beige Polo',
                category='shirts',
                price=50.00,
                description='',
                images=['shirt-4.jpg', 'shirt-4-alt.jpg'],
                sizes=['M', 'L', 'XL'],
                stock=50
            ),
            Product(
                name='White/Beige Polo',
                category='shirts',
                price=50.00,
                description='',
                images=['shirt-5.jpg', 'shirt-5-alt.jpg'],
                sizes=['M', 'L', 'XL'],
                stock=50
            ),
            # Crewnecks
            Product(
                name='Equalitie Crewneck',
                category='crewnecks',
                price=75.00,
                description='',
                images=['crew-1.jpg', 'crew-1-alt.jpg'],
                sizes=['M', 'L', 'XL'],
                stock=30
            ),
        ]

        for product in sample_products:
            db.session.add(product)
        db.session.commit()
        print("Sample products added to database!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)