from marshmallow import Schema, fields, validate, ValidationError

class CommentSchema(Schema):
    """Schema for validating and serializing comment data."""
    id = fields.Integer(dump_only=True)
    content = fields.String(required=True, validate=validate.Length(min=1))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    task_id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    # Add these fields for showing the username in comments
    username = fields.String(dump_only=True, attribute="user.username")