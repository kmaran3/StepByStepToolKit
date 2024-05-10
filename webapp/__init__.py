from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'xf8x03xf4'
    # Import and register blueprints or routes
    from .views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
