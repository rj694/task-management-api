from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60 per minute"],
)

# Import mail after other extensions but before create_app
from app.utils.email import mail

def create_app(config_object='app.config.DevelopmentConfig'):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_object)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)  # Initialize Flask-Mail
    
    # Import models to ensure they're registered with SQLAlchemy
    from app.models.user import User
    from app.models.task import Task
    from app.models.token_blacklist import TokenBlacklist
    from app.models.tag import Tag
    from app.models.comment import Comment
    from app.models.password_reset import PasswordResetToken
    from app.models.activity_log import ActivityLog
    
    # Register blueprints
    from app.resources.auth import auth_bp
    from app.resources.task import task_bp
    from app.resources.admin import admin_bp
    from app.resources.tag import tag_bp
    from app.resources.comment import comment_bp
    from app.resources.export import export_bp
    from app.utils.api_docs import api_docs_bp
    from app.resources.debug import debug_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(task_bp, url_prefix='/api/v1/tasks')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(tag_bp, url_prefix='/api/v1/tags')
    app.register_blueprint(comment_bp, url_prefix='/api/v1')
    app.register_blueprint(export_bp, url_prefix='/api/v1')
    app.register_blueprint(api_docs_bp, url_prefix='/api/v1/docs')
    app.register_blueprint(debug_bp, url_prefix='/api/v1/debug')
    
    # Register CLI commands
    from app.cli import register_commands
    register_commands(app)
    
    # Register error handlers
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)
    
    # JWT token blacklist loader
    from app.models.token_blacklist import TokenBlacklist
    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """Check if token is revoked."""
        return TokenBlacklist.is_token_revoked(jwt_payload)
    
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
            'message': f'Signature verification failed: {error}'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Authorization required',
            'message': f'Token is missing: {error}'
        }), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token has been revoked',
            'message': 'Please log in again'
        }), 401
        
    # Add this new handler for wrong token type
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Fresh token required',
            'message': 'Fresh token required'
        }), 401
        
    # This is specifically for the refresh vs access token issue
    # We'll patch the auth.py to handle this correctly
    
    # Rate limiter error handler
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later."
        }), 429
    
    # Shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {"app": app, "db": db, "TokenBlacklist": TokenBlacklist}
    
    # Root route
    @app.route('/')
    def index():
        return jsonify({
            "message": "Welcome to the Task Management API",
            "version": "1.0.0",
            "documentation": "/api/v1/docs"
        }), 200
    
    return app