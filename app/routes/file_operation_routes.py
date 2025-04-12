# fastique/app/routes/file_operation_routes.py
# Routes for file operations

from flask import Blueprint, request, jsonify, current_app
from app.search.file_operations import FileOperations, FileOperationError
import os

file_op_bp = Blueprint('file_operations', __name__, url_prefix='/file')

@file_op_bp.route('/info', methods=['GET'])
def get_file_info():
    """Get information about a file or directory"""
    path = request.args.get('path')
    
    if not path:
        return jsonify({'error': 'No path provided'}), 400
    
    try:
        info = FileOperations.get_file_info(path)
        return jsonify({'success': True, 'info': info})
    except FileOperationError as e:
        return jsonify({'error': str(e)}), 400

@file_op_bp.route('/open', methods=['POST'])
def open_file():
    """Open a file with the default application"""
    data = request.json
    path = data.get('path')
    
    if not path:
        return jsonify({'error': 'No path provided'}), 400
    
    try:
        FileOperations.open_file(path)
        return jsonify({'success': True})
    except FileOperationError as e:
        return jsonify({'error': str(e)}), 400

@file_op_bp.route('/copy', methods=['POST'])
def copy_file():
    """Copy a file or directory"""
    data = request.json
    source = data.get('source')
    destination = data.get('destination')
    
    if not source or not destination:
        return jsonify({'error': 'Source and destination paths are required'}), 400
    
    try:
        FileOperations.copy_file(source, destination)
        return jsonify({'success': True, 'destination': destination})
    except FileOperationError as e:
        return jsonify({'error': str(e)}), 400

@file_op_bp.route('/move', methods=['POST'])
def move_file():
    """Move a file or directory"""
    data = request.json
    source = data.get('source')
    destination = data.get('destination')
    
    if not source or not destination:
        return jsonify({'error': 'Source and destination paths are required'}), 400
    
    try:
        FileOperations.move_file(source, destination)
        return jsonify({'success': True, 'destination': destination})
    except FileOperationError as e:
        return jsonify({'error': str(e)}), 400

@file_op_bp.route('/rename', methods=['POST'])
def rename_file():
    """Rename a file or directory"""
    data = request.json
    path = data.get('path')
    new_name = data.get('new_name')
    
    if not path or not new_name:
        return jsonify({'error': 'Path and new name are required'}), 400
    
    try:
        new_path = FileOperations.rename_file(path, new_name)
        return jsonify({'success': True, 'new_path': new_path})
    except FileOperationError as e:
        return jsonify({'error': str(e)}), 400

@file_op_bp.route('/delete', methods=['POST'])
def delete_file():
    """Delete a file or directory"""
    data = request.json
    path = data.get('path')
    use_trash = data.get('use_trash', True)
    
    if not path:
        return jsonify({'error': 'Path is required'}), 400
    
    try:
        FileOperations.delete_file(path, use_trash)
        return jsonify({'success': True})
    except FileOperationError as e:
        return jsonify({'error': str(e)}), 400

@file_op_bp.route('/create_folder', methods=['POST'])
def create_folder():
    """Create a new folder"""
    data = request.json
    path = data.get('path')
    
    if not path:
        return jsonify({'error': 'Path is required'}), 400
    
    try:
        FileOperations.create_folder(path)
        return jsonify({'success': True, 'path': path})
    except FileOperationError as e:
        return jsonify({'error': str(e)}), 400

@file_op_bp.route('/create_file', methods=['POST'])
def create_file():
    """Create a new file"""
    data = request.json
    path = data.get('path')
    content = data.get('content', '')
    
    if not path:
        return jsonify({'error': 'Path is required'}), 400
    
    try:
        FileOperations.create_file(path, content)
        return jsonify({'success': True, 'path': path})
    except FileOperationError as e:
        return jsonify({'error': str(e)}), 400