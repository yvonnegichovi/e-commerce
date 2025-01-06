"""
This file contains notifications, emailing, texting and whatsapp
"""

from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
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

