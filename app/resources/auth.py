from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity, get_jwt, verify_jwt_in_request
)
from marshmallow import ValidationError
from datetime import datetime, timezone
from app import db, limiter
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.models.password_reset import PasswordResetToken
from app.schemas import user_registration_schema, user_login_schema, user_schema
from app.utils.email import send_password_reset_email, send_password_reset_confirmation_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("10 per hour")
def register():
    """Register a new user."""
    try:
        # Validate and deserialise input
        data = user_registration_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "User with this email already exists"}), 409
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "User with this username already exists"}), 409
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        role=data.get('role', 'user')  # Default to 'user' role
    )
    
    # Add user to database
    db.session.add(user)
    db.session.commit()
    
    # Create tokens - IMPORTANT: Convert user.id to string
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        "message": "User registered successfully",
        "user": user_schema.dump(user),
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 201

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("20 per hour")
def login():
    """Login a user."""
    try:
        # Validate and deserialise input
        data = user_login_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400
    
    # Check if user exists
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Create tokens - IMPORTANT: Convert user.id to string
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        "message": "Login successful",
        "user": user_schema.dump(user),
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@limiter.limit("20 per minute")
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    
    return jsonify({
        "access_token": access_token
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout a user by revoking their token."""
    jwt_payload = get_jwt()
    jti = jwt_payload['jti']
    user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(user_id, str):
        user_id = int(user_id)
    
    # Add token to blacklist
    token_type = jwt_payload['type']
    expires_at = datetime.fromtimestamp(jwt_payload['exp'], timezone.utc)
    
    token_blacklist = TokenBlacklist(
        jti=jti,
        token_type=token_type,
        user_id=user_id,
        expires_at=expires_at
    )
    
    db.session.add(token_blacklist)
    db.session.commit()
    
    return jsonify({
        "message": "Successfully logged out"
    }), 200

@auth_bp.route('/logout/all', methods=['POST'])
@limiter.limit("5 per hour")
@jwt_required()
def logout_all():
    """Logout from all devices by blacklisting all user tokens."""
    user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(user_id, str):
        user_id = int(user_id)
    
    # Add current token to blacklist
    jwt_payload = get_jwt()
    jti = jwt_payload['jti']
    token_type = jwt_payload['type']
    expires_at = datetime.fromtimestamp(jwt_payload['exp'], timezone.utc)
    
    token_blacklist = TokenBlacklist(
        jti=jti,
        token_type=token_type,
        user_id=user_id,
        expires_at=expires_at
    )
    
    db.session.add(token_blacklist)
    
    # Note: In a real production app, you might want to implement a mechanism to 
    # blacklist all existing tokens for a user. This would require maintaining 
    # a list of all active tokens or using a timestamp approach.
    
    db.session.commit()
    
    return jsonify({
        "message": "Successfully logged out from all devices"
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """Get current user details."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
        
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user_schema.dump(user)), 200

@auth_bp.route('/me', methods=['PUT'])
@limiter.limit("20 per hour")
@jwt_required()
def update_me():
    """Update current user details."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
        
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get the updates from the request
    data = request.json
    
    # Update username if provided and not taken
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already taken"}), 409
        user.username = data['username']
    
    # Update email if provided and not taken
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already taken"}), 409
        user.email = data['email']
    
    # Update password if provided
    if 'password' in data:
        user.set_password(data['password'])
    
    # Save changes
    db.session.commit()
    
    return jsonify({
        "message": "User updated successfully",
        "user": user_schema.dump(user)
    }), 200

@auth_bp.route('/forgot-password', methods=['POST'])
@limiter.limit("5 per hour")
def forgot_password():
    """Request a password reset."""
    data = request.get_json()
    
    if not data or 'email' not in data:
        return jsonify({"error": "Email is required"}), 400
    
    email = data['email']
    user = User.query.filter_by(email=email).first()
    
    # Always return success to prevent email enumeration
    if user:
        # Create password reset token
        reset_token = PasswordResetToken(user_id=user.id)
        db.session.add(reset_token)
        db.session.commit()
        
        # Send password reset email
        try:
            send_password_reset_email(user, reset_token.token)
        except Exception as e:
            # Log the error but don't expose it to the user
            print(f"Error sending password reset email: {str(e)}")
    
    return jsonify({
        "message": "If an account exists with this email, you will receive password reset instructions."
    }), 200

@auth_bp.route('/reset-password', methods=['POST'])
@limiter.limit("10 per hour")
def reset_password():
    """Reset password using token."""
    data = request.get_json()
    
    if not data or 'token' not in data or 'password' not in data:
        return jsonify({"error": "Token and new password are required"}), 400
    
    token = data['token']
    new_password = data['password']
    
    # Validate password length
    if len(new_password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400
    
    # Get valid token
    reset_token = PasswordResetToken.get_valid_token(token)
    
    if not reset_token:
        return jsonify({"error": "Invalid or expired token"}), 400
    
    # Get user
    user = User.query.get(reset_token.user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Update password
    user.set_password(new_password)
    
    # Mark token as used
    reset_token.mark_as_used()
    
    # Save changes
    db.session.commit()
    
    # Send confirmation email
    try:
        send_password_reset_confirmation_email(user)
    except Exception as e:
        # Log the error but don't fail the request
        print(f"Error sending confirmation email: {str(e)}")
    
    return jsonify({
        "message": "Password reset successfully"
    }), 200

@auth_bp.route('/verify-reset-token', methods=['POST'])
def verify_reset_token():
    """Verify if a password reset token is valid."""
    data = request.get_json()
    
    if not data or 'token' not in data:
        return jsonify({"error": "Token is required"}), 400
    
    token = data['token']
    reset_token = PasswordResetToken.get_valid_token(token)
    
    if reset_token:
        return jsonify({
            "valid": True,
            "message": "Token is valid"
        }), 200
    else:
        return jsonify({
            "valid": False,
            "message": "Invalid or expired token"
        }), 200