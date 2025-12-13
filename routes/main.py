from flask import Blueprint, render_template, request, jsonify
from models import db, Product

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    return render_template('home.html')


@main_bp.route('/shop')
def shop():
    category = request.args.get('category', 'all')

    if category == 'all':
        products = Product.query.all()
    else:
        products = Product.query.filter_by(category=category).all()

    return render_template('shop.html', products=products, current_category=category)


@main_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Handle contact form submission
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # TODO: Implement email sending or store in database
        return jsonify({'success': True, 'message': 'Thank you for your message!'})

    return render_template('contact.html')


@main_bp.route('/size-guide')
def size_guide():
    return render_template('size-guide.html')


@main_bp.route('/returns')
def returns():
    return render_template('returns.html')
@main_bp.route('/admin/orders')
def admin_orders():
    """View all orders - basic auth protected"""
    import os
    from flask import request, Response
    from models import Order

    # Check for Basic Authentication
    auth = request.authorization

    correct_username = os.getenv('ADMIN_USERNAME')
    correct_password = os.getenv('ADMIN_PASSWORD')

    if not auth or auth.username != correct_username or auth.password != correct_password:
        return Response(
            'Access denied', 401,
            {'WWW-Authenticate': 'Basic realm="Admin Area"'}
        )

    orders = Order.query.order_by(Order.created_at.desc()).all()

    html = "<h1>Orders</h1>"
    for order in orders:
        html += f"<div style='border:1px solid #ccc; padding:10px; margin:10px;'>"
        html += f"<strong>{order.order_number}</strong><br>"
        html += f"Customer: {order.first_name} {order.last_name}<br>"
        html += f"Email: {order.email}<br>"
        html += f"Total: ${order.total:.2f}<br>"
        html += f"Status: {order.payment_status}<br>"
        html += f"Date: {order.created_at}<br>"
        html += "</div>"

    return html