from app import create_app
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity
from flask import current_app
import os

def debug_jwt():
    """Debug JWT token generation and verification."""
    app = create_app()
    
    with app.app_context():
        # Print environment variables and configuration
        print("=== ENVIRONMENT VARIABLES ===")
        print(f"JWT_SECRET_KEY from env: '{os.environ.get('JWT_SECRET_KEY')}'")
        print(f"SECRET_KEY from env: '{os.environ.get('SECRET_KEY')}'")
        
        print("\n=== FLASK CONFIG ===")
        print(f"JWT_SECRET_KEY from config: '{app.config.get('JWT_SECRET_KEY')}'")
        print(f"JWT_ALGORITHM from config: '{app.config.get('JWT_ALGORITHM')}'")
        print(f"JWT_HEADER_TYPE from config: '{app.config.get('JWT_HEADER_TYPE')}'")
        print(f"JWT_TOKEN_LOCATION from config: '{app.config.get('JWT_TOKEN_LOCATION')}'")
        
        # Generate a token with string identity
        print("\n=== GENERATING TOKEN WITH STRING IDENTITY ===")
        user_id = 1
        access_token = create_access_token(identity=str(user_id))
        print(f"Generated token: {access_token}")
        
        # Try to decode the token
        print("\n=== DECODING TOKEN ===")
        try:
            decoded_token = decode_token(access_token)
            print(f"Successfully decoded token: {decoded_token}")
            
            # Extract identity
            print(f"Identity from token: {decoded_token.get('sub')}")
        except Exception as e:
            print(f"Failed to decode token: {str(e)}")

if __name__ == "__main__":
    debug_jwt()