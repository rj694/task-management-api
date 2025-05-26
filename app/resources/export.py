from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
import csv
from io import StringIO
from app.models.task import Task
from app.models.tag import Tag
from app.schemas import tasks_schema

export_bp = Blueprint('export', __name__)

@export_bp.route('/tasks/export', methods=['GET'])
@jwt_required()
def export_tasks():
    """Export tasks in different formats (json, csv)."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    # Get format parameter
    export_format = request.args.get('format', 'json').lower()
    
    # Get optional filters
    status = request.args.get('status')
    priority = request.args.get('priority')
    tag_id = request.args.get('tag_id')
    
    # Base query
    query = Task.query.filter_by(user_id=current_user_id)
    
    # Apply filters if provided
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    if tag_id:
        query = query.join(Task.tags).filter(Tag.id == tag_id)
    
    # Get all tasks
    tasks = query.all()
    
    if export_format == 'json':
        # Serialize tasks to JSON
        serialized_tasks = tasks_schema.dump(tasks)
        return jsonify(serialized_tasks)
    
    elif export_format == 'csv':
        # Prepare CSV data
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header row
        writer.writerow(['ID', 'Title', 'Description', 'Status', 'Priority', 'Due Date', 'Created At', 'Updated At', 'Tags'])
        
        # Write data rows
        for task in tasks:
            # Get tags as comma-separated string
            tags_str = ', '.join([tag.name for tag in task.tags])
            
            writer.writerow([
                task.id,
                task.title,
                task.description or '',  # Handle None values
                task.status,
                task.priority,
                task.due_date.isoformat() if task.due_date else '',
                task.created_at.isoformat(),
                task.updated_at.isoformat(),
                tags_str
            ])
        
        # Prepare response
        response = Response(output.getvalue(), mimetype='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=tasks.csv'
        
        return response
    
    else:
        return jsonify({
            "error": "Unsupported export format",
            "supported_formats": ["json", "csv"]
        }), 400