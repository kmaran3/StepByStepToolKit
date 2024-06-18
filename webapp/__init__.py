from flask import Flask
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy

# Initialize the database globally
db = SQLAlchemy()

# Define a basic user class
class User(UserMixin, db.Model):
    id = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(100))

    def __init__(self, id, password):
        self.id = id
        self.password = password

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-very-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database with the current app
    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # User loader function
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    from .views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
