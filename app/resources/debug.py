from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, get_jwt
import jwt
from flask import current_app

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/auth-test', methods=['GET'])
def auth_test():
    """Test authentication without JWT requirement."""
    auth_header = request.headers.get('Authorization', '')
    
    debug_info = {
        "has_auth_header": auth_header != '',
        "auth_header": auth_header,
        "all_headers": dict(request.headers),
        "flask_jwt_settings": {
            "secret_key": current_app.config.get('JWT_SECRET_KEY'),
            "algorithm": current_app.config.get('JWT_ALGORITHM', 'HS256'),
            "header_type": current_app.config.get('JWT_HEADER_TYPE'),
            "token_location": current_app.config.get('JWT_TOKEN_LOCATION')
        }
    }
    
    # Try to manually verify the token
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        debug_info["token"] = token
        
        try:
            # Try to manually decode token
            decoded = jwt.decode(
                token, 
                current_app.config.get('JWT_SECRET_KEY'), 
                algorithms=[current_app.config.get('JWT_ALGORITHM', 'HS256')]
            )
            debug_info["manual_decode"] = {
                "success": True,
                "decoded": decoded
            }
        except Exception as e:
            debug_info["manual_decode"] = {
                "success": False,
                "error": str(e)
            }
        
        # Try Flask-JWT-Extended verification
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            jwt_data = get_jwt()
            debug_info["jwt_extended_verify"] = {
                "success": True,
                "user_id": user_id,
                "jwt_data": jwt_data
            }
        except Exception as e:
            debug_info["jwt_extended_verify"] = {
                "success": False,
                "error": str(e)
            }
    
    return jsonify(debug_info), 200

@debug_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    """A protected endpoint that requires JWT."""
    current_user_id = get_jwt_identity()
    return jsonify({
        "message": "Access granted to protected endpoint!",
        "user_id": current_user_id
    }), 200