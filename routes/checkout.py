from flask import Blueprint, render_template, request, jsonify, current_app
from models import db, CartItem, Order
from routes.cart import get_session_id
import uuid
from datetime import datetime

checkout_bp = Blueprint('checkout', __name__)


@checkout_bp.route('/')
def checkout():
    session_id = get_session_id()
    cart_items = CartItem.query.filter_by(session_id=session_id).all()

    if not cart_items:
        return render_template('checkout.html', cart_empty=True)

    items = []
    subtotal = 0

    for item in cart_items:
        item_dict = item.to_dict()
        item_total = item.product.price * item.quantity
        item_dict['total'] = item_total
        items.append(item_dict)
        subtotal += item_total

    return render_template('checkout.html',
                           cart_items=items,
                           subtotal=subtotal,
                           shipping=0.00,
                           total=subtotal,
                           stripe_public_key=current_app.config['STRIPE_PUBLIC_KEY'])


@checkout_bp.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    """
    Create a Stripe Payment Intent
    Add your Stripe integration here
    """
    try:
        data = request.get_json()

        # TODO: Implement Stripe payment intent creation
        # Example structure:
        # import stripe
        # stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        #
        # intent = stripe.PaymentIntent.create(
        #     amount=int(data['amount'] * 100),  # Convert to cents
        #     currency='usd',
        #     metadata={'order_number': data['order_number']}
        # )
        #
        # return jsonify({
        #     'clientSecret': intent.client_secret
        # })

        return jsonify({
            'success': False,
            'message': 'Stripe not configured. Add your API keys in app.py'
        }), 501

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@checkout_bp.route('/process', methods=['POST'])
def process_checkout():
    """Process the checkout and create an order"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'firstName', 'lastName', 'address', 'city', 'state', 'zip']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing {field}'}), 400

        session_id = get_session_id()
        cart_items = CartItem.query.filter_by(session_id=session_id).all()

        if not cart_items:
            return jsonify({'success': False, 'message': 'Cart is empty'}), 400

        # Calculate totals
        items = []
        subtotal = 0

        for item in cart_items:
            item_data = {
                'product_name': item.product.name,
                'product_id': item.product.id,
                'size': item.size,
                'quantity': item.quantity,
                'price': item.product.price,
                'total': item.product.price * item.quantity
            }
            items.append(item_data)
            subtotal += item_data['total']

        # Generate unique order number
        order_number = f"EQ{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"

        # Create order
        order = Order(
            order_number=order_number,
            email=data['email'],
            first_name=data['firstName'],
            last_name=data['lastName'],
            address=data['address'],
            city=data['city'],
            state=data['state'],
            zip_code=data['zip'],
            items=items,
            subtotal=subtotal,
            total=subtotal  # Free shipping
        )

        db.session.add(order)

        # Clear cart after successful order
        for item in cart_items:
            db.session.delete(item)

        db.session.commit()

        return jsonify({
            'success': True,
            'order_number': order_number,
            'message': 'Order placed successfully!'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@checkout_bp.route('/success/<order_number>')
def order_success(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('order-success.html', order=order)


@checkout_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """
    Handle Stripe webhooks
    Add your webhook handling here
    """
    # TODO: Implement Stripe webhook handling
    # Example structure:
    # import stripe
    #
    # payload = request.data
    # sig_header = request.headers.get('Stripe-Signature')
    #
    # try:
    #     event = stripe.Webhook.construct_event(
    #         payload, sig_header, current_app.config['STRIPE_WEBHOOK_SECRET']
    #     )
    #
    #     if event['type'] == 'payment_intent.succeeded':
    #         payment_intent = event['data']['object']
    #         # Update order status
    #
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 400
    #
    # return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'Webhook not configured'}), 501