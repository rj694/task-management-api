from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()

def create_app(config_object='app.config.DevelopmentConfig'):
    """Application factory pattern.
    
    Args:
        config_object (str): The configuration object to use.
        
    Returns:
        app: Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_object)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    
    # Register blueprints
    from app.resources.auth import auth_bp
    from app.resources.task import task_bp
    from app.utils.api_docs import api_docs_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(task_bp, url_prefix='/api/v1/tasks')
    app.register_blueprint(api_docs_bp, url_prefix='/api/v1/docs')
    
    # Register CLI commands
    from app.cli import register_commands
    register_commands(app)
    
    # Register error handlers
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token has expired',
            'message': 'Please log in again'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Invalid token',
            'message': 'Signature verification failed'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Authorization required',
            'message': 'Token is missing'
        }), 401
    
    # Shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {"app": app, "db": db}
    
    # Root route
    @app.route('/')
    def index():
        return jsonify({
            "message": "Welcome to the Task Management API",
            "version": "1.0.0",
            "documentation": "/api/v1/docs"
        }), 200
    
    return app