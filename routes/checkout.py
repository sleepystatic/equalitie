from flask import Blueprint, render_template, request, jsonify, current_app
from models import db, CartItem, Order
from routes.cart import get_session_id
import stripe
from datetime import datetime
import uuid

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
        sale_price = round(item.product.price * 0.40, 2)
        item_total = sale_price * item.quantity

        item_dict = {
            'product': item.product,
            'size': item.size,
            'quantity': item.quantity,
            'total': item_total
        }

        items.append(item_dict)
        subtotal += item_total

    return render_template('checkout.html',
                           cart_items=items,
                           subtotal=subtotal,
                           shipping=0.00,
                           total=subtotal,
                           stripe_public_key=current_app.config['STRIPE_PUBLIC_KEY'])


@checkout_bp.route('/process', methods=['POST'])
def process_checkout():
    """Process the checkout and create an order"""
    try:
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'firstName', 'lastName', 'address', 'city', 'state', 'zip', 'payment_method_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing {field}'}), 400

        session_id = get_session_id()
        cart_items = CartItem.query.filter_by(session_id=session_id).all()

        if not cart_items:
            return jsonify({'success': False, 'message': 'Cart is empty'}), 400

        # Calculate totals with discount
        items = []
        subtotal = 0

        for item in cart_items:
            sale_price = round(item.product.price * 0.40, 2)

            item_data = {
                'product_name': item.product.name,
                'product_id': item.product.id,
                'size': item.size,
                'quantity': item.quantity,
                'price': sale_price,
                'total': sale_price * item.quantity
            }
            items.append(item_data)
            subtotal += sale_price * item.quantity

        # Generate unique order number
        order_number = f"EQ{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"

        # CHARGE THE CARD - THIS IS THE CRITICAL PART
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(subtotal * 100),  # Convert to cents
                currency='usd',
                payment_method=data['payment_method_id'],
                confirm=True,
                receipt_email=data['email'],
                description=f'Order {order_number}',
                metadata={
                    'order_number': order_number,
                    'customer_name': f"{data['firstName']} {data['lastName']}"
                },
                automatic_payment_methods={
                    'enabled': True,
                    'allow_redirects': 'never'
                }
            )

            # CRITICAL SECURITY CHECK
            if payment_intent.status != 'succeeded':
                return jsonify({
                    'success': False,
                    'message': f'Payment was not successful. Status: {payment_intent.status}'
                }), 400

        except stripe.error.CardError as e:
            # Card was declined
            return jsonify({
                'success': False,
                'message': f'Your card was declined: {e.user_message}'
            }), 400

        except stripe.error.StripeError as e:
            # Other Stripe errors
            return jsonify({
                'success': False,
                'message': f'Payment error: {str(e)}'
            }), 400

        # ONLY CREATE ORDER IF PAYMENT SUCCEEDED
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
            total=subtotal
        )
        order.stripe_payment_intent = payment_intent.id
        order.payment_status = 'succeeded'

        db.session.add(order)

        # Clear cart after successful payment
        for item in cart_items:
            db.session.delete(item)

        db.session.commit()

        return jsonify({
            'success': True,
            'order_number': order_number,
            'message': 'Payment successful!'
        })

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        print(f"Checkout error: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred. Please try again.'}), 500
@checkout_bp.route('/success/<order_number>')
def order_success(order_number):
    """Display order success page"""
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('order-success.html', order=order)