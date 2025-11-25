from flask import Blueprint, request, jsonify, session
from models import db, Product, CartItem
import uuid

cart_bp = Blueprint('cart', __name__)


def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session.permanent = True
    return session['session_id']


@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    size = data.get('size')

    if not product_id or not size:
        return jsonify({'success': False, 'message': 'Missing product or size'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'}), 404

    session_id = get_session_id()

    # Check if item already exists in cart
    cart_item = CartItem.query.filter_by(
        session_id=session_id,
        product_id=product_id,
        size=size
    ).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(
            session_id=session_id,
            product_id=product_id,
            size=size,
            quantity=1
        )
        db.session.add(cart_item)

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Item added to cart',
        'cart_count': get_cart_count()
    })


@cart_bp.route('/remove/<int:item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    session_id = get_session_id()
    cart_item = CartItem.query.filter_by(id=item_id, session_id=session_id).first()

    if not cart_item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404

    db.session.delete(cart_item)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Item removed from cart',
        'cart_count': get_cart_count()
    })


@cart_bp.route('/update/<int:item_id>', methods=['PUT'])
def update_cart_item(item_id):
    data = request.get_json()
    quantity = data.get('quantity', 1)

    session_id = get_session_id()
    cart_item = CartItem.query.filter_by(id=item_id, session_id=session_id).first()

    if not cart_item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404

    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Cart updated',
        'cart_count': get_cart_count()
    })


@cart_bp.route('/items')
def get_cart_items():
    session_id = get_session_id()
    cart_items = CartItem.query.filter_by(session_id=session_id).all()

    items = []
    subtotal = 0

    for item in cart_items:
        item_dict = item.to_dict()
        sale_price = round(item.product.price * 0.40, 2)  # ← Calculate sale price
        item_total = sale_price * item.quantity  # ← Use sale price
        item_dict['total'] = item_total
        items.append(item_dict)
        subtotal += item_total

    return jsonify({
        'items': items,
        'subtotal': subtotal,
        'shipping': 0.00,  # Free shipping
        'total': subtotal,
        'count': len(items)
    })


@cart_bp.route('/count')
def cart_count():
    return jsonify({'count': get_cart_count()})


def get_cart_count():
    session_id = get_session_id()
    return CartItem.query.filter_by(session_id=session_id).count()