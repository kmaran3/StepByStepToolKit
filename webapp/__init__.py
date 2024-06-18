from flask import Flask
from flask_login import LoginManager, UserMixin

# Create the Flask application
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-very-secret-key'

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # Define a basic user class
    class User(UserMixin):
        def __init__(self, id):
            self.id = id

    # Dictionary to simulate user database
    users = {
        'user1': {'id': 'user1', 'password': 'secret'}
    }

    # User loader function
    @login_manager.user_loader
    def load_user(user_id):
        if user_id in users:
            return User(user_id)
        return None

    from .views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
