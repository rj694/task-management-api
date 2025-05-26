from marshmallow import Schema, fields, validate, ValidationError

class TagSchema(Schema):
    """Schema for validating and serializing tag data."""
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    color = fields.String(validate=validate.Regexp(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'))
    user_id = fields.Integer(dump_only=True)

class TagReferenceSchema(Schema):
    """Schema for referencing tags in other schemas."""
    id = fields.Integer(required=True)