import os
from dotenv import load_dotenv
from flask import Flask
from config import Config
from app.extensions import db, login_manager

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(BASE_DIR, 'templates'),
                static_folder=os.path.join(BASE_DIR, 'static'))
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.dashboard.routes import dashboard_bp
    from app.learning.routes import learning_bp
    from app.chatbot.routes import chatbot_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(learning_bp, url_prefix='/learning')
    app.register_blueprint(chatbot_bp)

    with app.app_context():
        import app.models
        db.create_all()

    return app
