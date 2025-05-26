from marshmallow import Schema, fields, validate, ValidationError

class UserRegistrationSchema(Schema):
    """Schema for validating user registration data."""
    username = fields.String(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    role = fields.String(validate=validate.OneOf(['user', 'admin']))

class UserLoginSchema(Schema):
    """Schema for validating user login data."""
    email = fields.Email(required=True)
    password = fields.String(required=True)

class UserSchema(Schema):
    """Schema for serializing user data."""
    id = fields.Integer(dump_only=True)
    username = fields.String(dump_only=True)
    email = fields.Email(dump_only=True)
    role = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)