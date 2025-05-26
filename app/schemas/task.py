from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime
from app.schemas.tag import TagSchema

class TaskSchema(Schema):
    """Schema for validating and serializing task data."""
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String()
    status = fields.String(validate=validate.OneOf(['pending', 'in_progress', 'completed']))
    priority = fields.String(validate=validate.OneOf(['low', 'medium', 'high']))
    due_date = fields.DateTime(format='iso')
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    tags = fields.Nested(TagSchema, many=True, dump_only=True)
    tag_ids = fields.List(fields.Integer(), load_only=True)
    
    @validates('due_date')
    def validate_due_date(self, value, **kwargs):
        """Validate that due_date is not in the past."""
        if value and value < datetime.utcnow():
            raise ValidationError('Due date cannot be in the past.')

class TaskQuerySchema(Schema):
    """Schema for validating task query parameters."""
    status = fields.String(validate=validate.OneOf(['pending', 'in_progress', 'completed']))
    priority = fields.String(validate=validate.OneOf(['low', 'medium', 'high']))
    search = fields.String()
    tag = fields.Integer()  # Tag ID to filter by
    due_before = fields.DateTime(format='iso')
    due_after = fields.DateTime(format='iso')
    sort_by = fields.String(validate=validate.OneOf(
        ['title', 'status', 'priority', 'due_date', 'created_at', 'updated_at']
    ))
    sort_order = fields.String(validate=validate.OneOf(['asc', 'desc']))
    page = fields.Integer(validate=validate.Range(min=1))
    per_page = fields.Integer(validate=validate.Range(min=1, max=100))

class TaskBulkDeleteSchema(Schema):
    """Schema for validating bulk delete data."""
    task_ids = fields.List(fields.Integer(), required=True, validate=validate.Length(min=1))

class TaskBulkUpdateSchema(Schema):
    """Schema for validating bulk update data."""
    task_ids = fields.List(fields.Integer(), required=True, validate=validate.Length(min=1))
    updates = fields.Dict(required=True)