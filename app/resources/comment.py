from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app import db
from app.models.comment import Comment
from app.models.task import Task
from app.schemas import comment_schema, comments_schema

comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/tasks/<int:task_id>/comments', methods=['GET'])
@jwt_required()
def get_task_comments(task_id):
    """Get all comments for a specific task."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    # Check if task exists and belongs to the user
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # Get comments for the task
    comments = Comment.query.filter_by(task_id=task_id).order_by(Comment.created_at).all()
    
    return jsonify(comments_schema.dump(comments)), 200

@comment_bp.route('/tasks/<int:task_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(task_id):
    """Create a new comment for a task."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    # Check if task exists and belongs to the user
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    try:
        # Validate and deserialise input
        data = comment_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400
    
    # Create new comment
    comment = Comment(
        content=data['content'],
        task_id=task_id,
        user_id=current_user_id
    )
    
    # Add comment to database
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        "message": "Comment created successfully",
        "comment": comment_schema.dump(comment)
    }), 201

@comment_bp.route('/comments/<int:comment_id>', methods=['GET'])
@jwt_required()
def get_comment(comment_id):
    """Get a specific comment."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    comment = Comment.query.filter_by(id=comment_id).first()
    
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    
    # Check if comment belongs to a task owned by the user
    task = Task.query.filter_by(id=comment.task_id, user_id=current_user_id).first()
    
    if not task:
        return jsonify({"error": "You do not have permission to access this comment"}), 403
    
    return jsonify(comment_schema.dump(comment)), 200

@comment_bp.route('/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    """Update a specific comment."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    comment = Comment.query.filter_by(id=comment_id).first()
    
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    
    # Check if comment belongs to the user
    if comment.user_id != current_user_id:
        return jsonify({"error": "You do not have permission to update this comment"}), 403
    
    try:
        # Validate and deserialise input
        data = comment_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400
    
    # Update comment content
    comment.content = data['content']
    
    # Update comment in database
    db.session.commit()
    
    return jsonify({
        "message": "Comment updated successfully",
        "comment": comment_schema.dump(comment)
    }), 200

@comment_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """Delete a specific comment."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    comment = Comment.query.filter_by(id=comment_id).first()
    
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    
    # Check if comment belongs to the user or if the user owns the task
    task = Task.query.filter_by(id=comment.task_id, user_id=current_user_id).first()
    
    if comment.user_id != current_user_id and not task:
        return jsonify({"error": "You do not have permission to delete this comment"}), 403
    
    # Delete comment from database
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({
        "message": "Comment deleted successfully"
    }), 200