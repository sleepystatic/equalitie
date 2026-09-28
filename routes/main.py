from flask import Blueprint, render_template, request, jsonify, Response
from models import db, Product
import csv
import io
import os

main_bp = Blueprint('main', __name__)


def _admin_auth_required():
    """Check HTTP Basic Auth credentials against environment variables."""
    auth = request.authorization
    correct_username = os.getenv('ADMIN_USERNAME')
    correct_password = os.getenv('ADMIN_PASSWORD')

    if not auth or auth.username != correct_username or auth.password != correct_password:
        return Response(
            'Access denied', 401,
            {'WWW-Authenticate': 'Basic realm="Admin Area"'}
        )
    return None


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
    """View all orders - basic auth protected."""
    from models import Order

    auth_error = _admin_auth_required()
    if auth_error:
        return auth_error

    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)


@main_bp.route('/admin/orders/export')
def admin_orders_export():
    """Export all orders as CSV - basic auth protected."""
    from models import Order

    auth_error = _admin_auth_required()
    if auth_error:
        return auth_error

    orders = Order.query.order_by(Order.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Order Number', 'Date', 'Email', 'First Name', 'Last Name',
        'Address', 'City', 'State', 'ZIP', 'Country', 'Items',
        'Subtotal', 'Total', 'Payment Status', 'Stripe Payment Intent'
    ])

    for order in orders:
        items_summary = ', '.join(
            f"{item['quantity']}x {item['product_name']} ({item['size']})"
            for item in order.get_items()
        )
        writer.writerow([
            order.order_number,
            order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else '',
            order.email,
            order.first_name,
            order.last_name,
            order.address,
            order.city,
            order.state,
            order.zip_code,
            order.country,
            items_summary,
            f"{order.subtotal:.2f}",
            f"{order.total:.2f}",
            order.payment_status,
            order.stripe_payment_intent or ''
        ])

    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=equalitie_orders.csv'}
    )


@main_bp.route('/admin/orders/<order_number>')
def admin_order_detail(order_number):
    """View a single order - basic auth protected."""
    from models import Order

    auth_error = _admin_auth_required()
    if auth_error:
        return auth_error

    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('admin/order_detail.html', order=order)