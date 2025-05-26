from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app import db
from app.models.tag import Tag
from app.schemas import tag_schema, tags_schema

tag_bp = Blueprint('tag', __name__)

@tag_bp.route('', methods=['GET'])
@jwt_required()
def get_tags():
    """Get all tags for the current user."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    tags = Tag.query.filter_by(user_id=current_user_id).all()
    
    return jsonify(tags_schema.dump(tags)), 200

@tag_bp.route('/<int:tag_id>', methods=['GET'])
@jwt_required()
def get_tag(tag_id):
    """Get a specific tag."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    tag = Tag.query.filter_by(id=tag_id, user_id=current_user_id).first()
    
    if not tag:
        return jsonify({"error": "Tag not found"}), 404
    
    return jsonify(tag_schema.dump(tag)), 200

@tag_bp.route('', methods=['POST'])
@jwt_required()
def create_tag():
    """Create a new tag."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    try:
        # Validate and deserialize input
        data = tag_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400
    
    # Check if tag with the same name already exists for this user
    existing_tag = Tag.query.filter_by(name=data['name'], user_id=current_user_id).first()
    if existing_tag:
        return jsonify({"error": "Tag with this name already exists"}), 409
    
    # Create new tag
    tag = Tag(
        name=data['name'],
        user_id=current_user_id,
        color=data.get('color', "#3498db")
    )
    
    # Add tag to database
    db.session.add(tag)
    db.session.commit()
    
    return jsonify({
        "message": "Tag created successfully",
        "tag": tag_schema.dump(tag)
    }), 201

@tag_bp.route('/<int:tag_id>', methods=['PUT'])
@jwt_required()
def update_tag(tag_id):
    """Update a specific tag."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    tag = Tag.query.filter_by(id=tag_id, user_id=current_user_id).first()
    
    if not tag:
        return jsonify({"error": "Tag not found"}), 404
    
    try:
        # Validate and deserialize input
        data = tag_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400
    
    # Check if new name conflicts with existing tag
    if 'name' in data and data['name'] != tag.name:
        existing_tag = Tag.query.filter_by(name=data['name'], user_id=current_user_id).first()
        if existing_tag:
            return jsonify({"error": "Tag with this name already exists"}), 409
        tag.name = data['name']
    
    # Update color if provided
    if 'color' in data:
        tag.color = data['color']
    
    # Update tag in database
    db.session.commit()
    
    return jsonify({
        "message": "Tag updated successfully",
        "tag": tag_schema.dump(tag)
    }), 200

@tag_bp.route('/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id):
    """Delete a specific tag."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    tag = Tag.query.filter_by(id=tag_id, user_id=current_user_id).first()
    
    if not tag:
        return jsonify({"error": "Tag not found"}), 404
    
    # Remove tag from database
    db.session.delete(tag)
    db.session.commit()
    
    return jsonify({
        "message": "Tag deleted successfully"
    }), 200