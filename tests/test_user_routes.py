import pytest
from entry import app, db
from entry.models import User 
from werkzeug.security import generate_password_hash

def test_login_success(client, standard_user):
    # Log in with correct credentials
    response = client.post('/login', data={
        'email': standard_user.email,
        'password': 'password123'  # This should match the password in your fixture
    }, follow_redirects=True)
    assert b"Login successful" in response.data
    assert b"Logged in successfully" in response.data

def test_login_failure(client):
    # Attempt login with incorrect credentials
    response = client.post('/login', data={
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert b"Invalid email or password" in response.data
