### File: C:\Users\rdjon\Downloads\task-management-api\app\utils\errors.py
from flask import jsonify
from marshmallow import ValidationError

def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request", "message": str(e)}), 400
    
    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Unauthorized", "message": str(e)}), 401
    
    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Forbidden", "message": str(e)}), 403
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "message": str(e)}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed", "message": str(e)}), 405
    
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Server error", "message": str(e)}), 500
    
    @app.errorhandler(ValidationError)
    def validation_error(e):
        return jsonify({"error": "Validation error", "messages": e.messages}), 400

def handle_exception(e):
    """Handle and format exceptions."""
    if isinstance(e, ValidationError):
        return jsonify({"error": "Validation error", "messages": e.messages}), 400
    
    return jsonify({"error": "An error occurred", "message": str(e)}), 500