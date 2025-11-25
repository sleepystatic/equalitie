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