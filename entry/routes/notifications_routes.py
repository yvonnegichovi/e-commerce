"""
This file contains notifications, emailing, texting and whatsapp
"""

from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from marshmallow import Schema, fields, ValidationError, validates
from entry.models import db, Product
from entry import app
from urllib.parse import quote
import requests
import os

notifications = Blueprint('notifications', __name__)

load_dotenv()

WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER')

class MessageSchema(Schema):
    """
    Validates the recipient, sender, and message content.
    """
    message = fields.Str(required=True)
    recipient = fields.Str(required=True)
    product_id = fields.Int(required=True)

    @validates('recipient')
    def validate_recipient(self, value):
        if not value.startswith('+'):
            raise ValidationError("Recipient must start with a '+' followed by the country code.")

@notifications.route('/notifications/send_message', methods=['POST'])
def send_message():
    """
    Route to send a message (e.g., to WhatsApp).
    Expects a JSON payload with 'message', 'recipient', and 'product_id'.
    """
    schema = MessageSchema()
    try:
        # Validate and load input data
        data = schema.load(request.get_json())
        app.logger.info(f"Validated data: {data}")

        # Retrieve product information
        product = Product.query.filter_by(id=data['product_id']).first()
        if not product:
            return jsonify({'status': 'error', 'message': 'Product not found.'}), 404

        # Prepare the message
        product_name = product.product_name
        product_url = f"http://127.0.0.1:5000/product/{product.id}"  # Product URL for the specific product
        message = f"Hello, I would like to enquire about {product_name}. You can check it out here: {product_url}"

        # Send the WhatsApp message URL
        whatsapp_url = f"https://wa.me/{data['recipient']}?text={message}"

        return jsonify({'status': 'success', 'message': f'Message sent to {data["recipient"]}', 'whatsapp_url': whatsapp_url}), 200

    except ValidationError as err:
        app.logger.error(f"Validation error: {err.messages}")
        return jsonify({'errors': err.messages}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal Server Error"}), 500

@notifications.route('/messages', methods=['GET'])
def get_messages():
    """Retrieve all notifications/messages."""
    # Logic to fetch messages
    return jsonify({'messages': []})

@notifications.route('/messages', methods=['POST'])
def create_message():
    """Send a new notification/message."""
    # Logic to send message
    return jsonify({'status': 'Message sent'})


@notifications.route('/notifications/share_message', methods=['POST'])
@login_required
def share_message():
    """
    Route to send a message when sharing.
    Expects a JSON payload with 'message', 'recipient' (for WhatsApp), 'product_id', and 'platform'.
    """
    try:
        # Parse incoming JSON data
        data = request.get_json()
        app.logger.info(f"Received payload: {data}")

        # Validate common fields
        product_id = data.get('product_id')
        platform = data.get('platform', '').lower()

        if not product_id:
            return jsonify({'status': 'error', 'message': 'Missing product_id.'}), 400
        product_id = int(product_id)
        if not isinstance(product_id, int):
            return jsonify({'status': 'error', 'message': 'Invalid product_id.'}), 400

        if not platform:
            return jsonify({'status': 'error', 'message': 'Platform is required.'}), 400

        # Retrieve product information
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            return jsonify({'status': 'error', 'message': 'Product not found.'}), 404

        # Prepare the message
        product_name = product.product_name
        product_url = f"http://127.0.0.1:5000/product/{product.id}"  # Product URL for the specific product
        message = f"Checkout this product {product_name} from Zed Beauty. You can check it out here: {product_url} and browse more content from www.zedbeauty.com"

        # Handle platform-specific logic
        share_url = ""
        if platform == 'whatsapp':
            recipient = data.get('recipient', '').strip()
            if recipient:
                # If recipient is provided, generate a share link for the recipient
                share_url = f"https://wa.me/{recipient}?text={message}"
            else:
                # If no recipient is provided, generate a generic WhatsApp share link
                share_url = f"https://api.whatsapp.com/send?text={message}"
        elif platform == 'x':
            share_url = f"https://twitter.com/intent/tweet?text={message}"
        elif platform == 'facebook':
            share_url = f"https://www.facebook.com/sharer/sharer.php?u={product_url}&quote={message}"
        elif platform == 'instagram':
            # Instagram does not support direct sharing; link to Instagram
            share_url = "https://www.instagram.com/"
        else:
            return jsonify({'status': 'error', 'message': 'Unsupported platform.'}), 400

        return jsonify({
            'status': 'success',
            'message': f'Share link generated for {platform}',
            'share_url': share_url,
            'platform': platform
        }), 200

    except Exception as e:
        app.logger.error(f"Error in share_message: {str(e)}")
        return jsonify({'status': 'error', 'message': 'An unexpected error occurred.'}), 500

