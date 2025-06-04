from app.schemas.user import UserRegistrationSchema, UserLoginSchema, UserSchema
from app.schemas.task import TaskSchema, TaskQuerySchema, TaskBulkDeleteSchema, TaskBulkUpdateSchema
from app.schemas.tag import TagSchema, TagReferenceSchema
from app.schemas.comment import CommentSchema

# Initialise schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_registration_schema = UserRegistrationSchema()
user_login_schema = UserLoginSchema()

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
task_query_schema = TaskQuerySchema()
task_bulk_delete_schema = TaskBulkDeleteSchema()
task_bulk_update_schema = TaskBulkUpdateSchema()

tag_schema = TagSchema()
tags_schema = TagSchema(many=True)
tag_reference_schema = TagReferenceSchema()

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)