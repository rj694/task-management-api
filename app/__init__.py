from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# --------------------------------------------------------------------- #
# Initialisation
# --------------------------------------------------------------------- #
load_dotenv()

db       = SQLAlchemy()
migrate  = Migrate()
jwt      = JWTManager()
cors     = CORS()
limiter  = Limiter(key_func=get_remote_address,
                   default_limits=["60 per minute"])

# Mail needs the app later
from app.utils.email import mail   # isort: skip

def create_app(config_object="app.config.DevelopmentConfig"):
    """Flask application-factory."""
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)

    # Import models so Alembic sees them
    from app.models import (  # noqa: F401
        user, task, tag, comment,
        token_blacklist, password_reset, activity_log
    )

    # ---------------------------------------- #
    # Blueprints
    # ---------------------------------------- #
    from app.resources.auth     import auth_bp
    from app.resources.task     import task_bp
    from app.resources.tag      import tag_bp
    from app.resources.comment  import comment_bp
    from app.resources.export   import export_bp
    from app.resources.admin    import admin_bp
    from app.resources.activity import activity_bp   # <-- NEW
    from app.utils.api_docs     import api_docs_bp
    from app.resources.debug    import debug_bp

    app.register_blueprint(auth_bp,     url_prefix="/api/v1/auth")
    app.register_blueprint(task_bp,     url_prefix="/api/v1/tasks")
    app.register_blueprint(tag_bp,      url_prefix="/api/v1/tags")
    app.register_blueprint(comment_bp,  url_prefix="/api/v1")
    app.register_blueprint(export_bp,   url_prefix="/api/v1")
    app.register_blueprint(admin_bp,    url_prefix="/api/v1/admin")
    app.register_blueprint(activity_bp, url_prefix="/api/v1")  # <-- NEW
    app.register_blueprint(api_docs_bp, url_prefix="/api/v1/docs")
    app.register_blueprint(debug_bp,    url_prefix="/api/v1/debug")

    # ---------------------------------------- #
    # JWT blacklist callback
    # ---------------------------------------- #
    from app.models.token_blacklist import TokenBlacklist

    @jwt.token_in_blocklist_loader
    def _is_token_revoked(jwt_header, jwt_payload):
        return TokenBlacklist.is_token_revoked(jwt_payload)

    # Error handlers & 429 handler already present elsewhere
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)

    # Shell context
    @app.shell_context_processor
    def _ctx():
        return dict(app=app, db=db)  # pragma: no cover

    # Root ping
    @app.route("/")
    def index():
        return jsonify({
            "message": "Welcome to the Task Management API",
            "version": "1.0.0"
        }), 200

    return app