import pytest
from entry import app as flask_app, db as flask_db
from entry.models import Admin, User
from flask_bcrypt import generate_password_hash

@pytest.fixture(scope='session')
def app():
    """Sets up the Flask application for testing."""
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory SQLite database
    flask_app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing

    # Establish application context
    with flask_app.app_context():
        flask_db.create_all()  # Create tables
        yield flask_app

        # Drop tables after tests
        flask_db.drop_all()

@pytest.fixture
def client(app):
    """Provides a test client for interacting with the Flask app."""
    return app.test_client()

@pytest.fixture
def database(app):
    """Provides access to the database within the app context."""
    with app.app_context():
        yield flask_db

@pytest.fixture
def admin_user(database):
    """Creates a test admin user in the database."""
    hashed_password = generate_password_hash('adminpassword').decode('utf-8')
    admin = Admin(email='admin@example.com', password_hash=hashed_password)
    database.session.add(admin)
    database.session.commit()
    return admin

@pytest.fixture
def regular_user(database):
    """Creates a test regular user in the database."""
    hashed_password = generate_password_hash('userpassword').decode('utf-8')
    user = User(email='user@example.com', password_hash=hashed_password)
    database.session.add(user)
    database.session.commit()
    return user
