import pytest
from entry import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_send_message(client):
    response = client.post('/notifications/send_message', json={
        'message': 'Hello!',
        'recipient': '+254733654109',
        'product_id': '1'
    })
    assert response.status_code == 200
    assert response.get_json() == {
        "status": "success",
        "message": "Message sent to +254733654109",
        "whatsapp_url": "https://wa.me/+254733654109?text=Hello%20Zed%20Beauty%2C%20I%20would%20like%20to%20enquire%20about%20Boss%20perfume"
    }
