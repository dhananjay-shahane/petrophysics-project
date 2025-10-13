import os
import json
import tempfile
import traceback
from pathlib import Path
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from utils.project_utils import create_project_structure
from utils.las_processor import LASProcessor

api = Blueprint('api', __name__)

WORKSPACE_ROOT = os.path.join(os.getcwd(), "petrophysics-workplace")
ALLOWED_EXTENSIONS = {'las', 'LAS'}

# Ensure workspace exists
Path(WORKSPACE_ROOT).mkdir(parents=True, exist_ok=True)

# Helper function to validate paths (prevents symlink traversal)
def validate_path(path_str):
    resolved = os.path.realpath(path_str)
    workspace = os.path.realpath(WORKSPACE_ROOT)
    return resolved.startswith(workspace)

# Project Management Routes
@api.route('/projects/create', methods=['POST'])
def create_project():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Invalid or missing JSON payload'}), 400
        
        project_name = data.get('name', '').strip()
        parent_path = data.get('path', WORKSPACE_ROOT).strip()
        
        if not project_name:
            return jsonify({'error': 'Project name is required'}), 400
        
        if not project_name.replace('-', '').replace('_', '').isalnum():
            return jsonify({'error': 'Project name can only contain letters, numbers, hyphens, and underscores'}), 400
        
        resolved_parent = os.path.abspath(parent_path)
        if not validate_path(resolved_parent):
            return jsonify({'error': 'Access denied: path outside petrophysics-workplace'}), 403
        
        if not os.path.exists(resolved_parent):
            return jsonify({'error': 'Parent directory does not exist'}), 400
        
        result = create_project_structure(project_name, resolved_parent)
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to create project: {str(e)}'}), 500

# Directory Management Routes
@api.route('/directories/list', methods=['GET'])
def list_directories():
    try:
        dir_path = request.args.get('path', WORKSPACE_ROOT)
        resolved_path = os.path.abspath(dir_path)
        
        if not validate_path(resolved_path):
            return jsonify({'error': 'Access denied: path outside petrophysics-workplace'}), 403
        
        if not os.path.exists(resolved_path):
            Path(WORKSPACE_ROOT).mkdir(parents=True, exist_ok=True)
            return jsonify({
                'currentPath': WORKSPACE_ROOT,
                'parentPath': WORKSPACE_ROOT,
                'directories': [],
                'canGoUp': False
            })
        
        if not os.path.isdir(resolved_path):
            return jsonify({'error': 'Path is not a directory'}), 400
        
        items = []
        for item in os.listdir(resolved_path):
            if not item.startswith('.'):
                item_path = os.path.join(resolved_path, item)
                if os.path.isdir(item_path):
                    items.append({'name': item, 'path': item_path})
        
        items.sort(key=lambda x: x['name'])
        can_go_up = resolved_path != WORKSPACE_ROOT
        
        return jsonify({
            'currentPath': resolved_path,
            'parentPath': os.path.dirname(resolved_path) if can_go_up else resolved_path,
            'directories': items,
            'canGoUp': can_go_up
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/directories/create', methods=['POST'])
def create_directory():
    try:
        data = request.json
        parent_path = data.get('parentPath', WORKSPACE_ROOT)
        folder_name = data.get('folderName', '').strip()
        
        if not folder_name:
            return jsonify({'error': 'Folder name is required'}), 400
        
        if not folder_name.replace('-', '').replace('_', '').isalnum():
            return jsonify({'error': 'Folder name can only contain letters, numbers, hyphens, and underscores'}), 400
        
        resolved_parent = os.path.abspath(parent_path)
        if not validate_path(resolved_parent):
            return jsonify({'error': 'Access denied: path outside petrophysics-workplace'}), 403
        
        new_folder_path = os.path.join(resolved_parent, folder_name)
        
        if os.path.exists(new_folder_path):
            return jsonify({'error': 'Folder already exists'}), 400
        
        os.makedirs(new_folder_path)
        
        return jsonify({
            'success': True,
            'message': 'Folder created successfully',
            'path': new_folder_path,
            'name': folder_name
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/directories/delete', methods=['DELETE'])
def delete_directory():
    try:
        data = request.json
        folder_path = data.get('folderPath', '').strip()
        
        if not folder_path:
            return jsonify({'error': 'Folder path is required'}), 400
        
        resolved_path = os.path.abspath(folder_path)
        if not validate_path(resolved_path):
            return jsonify({'error': 'Access denied: path outside petrophysics-workplace'}), 403
        
        if resolved_path == WORKSPACE_ROOT:
            return jsonify({'error': 'Cannot delete workspace root'}), 403
        
        if not os.path.exists(resolved_path):
            return jsonify({'error': 'Folder not found'}), 404
        
        if not os.path.isdir(resolved_path):
            return jsonify({'error': 'Path is not a directory'}), 400
        
        import shutil
        shutil.rmtree(resolved_path)
        
        return jsonify({
            'success': True,
            'message': 'Folder deleted successfully',
            'path': resolved_path
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/directories/rename', methods=['PUT'])
def rename_directory():
    try:
        data = request.json
        folder_path = data.get('folderPath', '').strip()
        new_name = data.get('newName', '').strip()
        
        if not folder_path:
            return jsonify({'error': 'Folder path is required'}), 400
        
        if not new_name:
            return jsonify({'error': 'New folder name is required'}), 400
        
        if not new_name.replace('-', '').replace('_', '').isalnum():
            return jsonify({'error': 'Folder name can only contain letters, numbers, hyphens, and underscores'}), 400
        
        resolved_path = os.path.abspath(folder_path)
        if not validate_path(resolved_path):
            return jsonify({'error': 'Access denied: path outside petrophysics-workplace'}), 403
        
        if resolved_path == WORKSPACE_ROOT:
            return jsonify({'error': 'Cannot rename workspace root'}), 403
        
        if not os.path.exists(resolved_path):
            return jsonify({'error': 'Folder not found'}), 404
        
        if not os.path.isdir(resolved_path):
            return jsonify({'error': 'Path is not a directory'}), 400
        
        parent_dir = os.path.dirname(resolved_path)
        new_path = os.path.join(parent_dir, new_name)
        
        if os.path.exists(new_path):
            return jsonify({'error': 'A folder with this name already exists'}), 400
        
        os.rename(resolved_path, new_path)
        
        return jsonify({
            'success': True,
            'message': 'Folder renamed successfully',
            'oldPath': resolved_path,
            'newPath': new_path,
            'newName': new_name
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Data Explorer Routes
@api.route('/data/list', methods=['GET'])
def list_data():
    try:
        dir_path = request.args.get('path')
        if not dir_path:
            return jsonify({'error': 'Path is required'}), 400
        
        resolved_path = os.path.abspath(dir_path)
        if not validate_path(resolved_path):
            return jsonify({'error': 'Access denied: path outside petrophysics-workplace'}), 403
        
        if not os.path.isdir(resolved_path):
            return jsonify({'error': 'Path is not a directory'}), 400
        
        items = []
        for item in os.listdir(resolved_path):
            if not item.startswith('.'):
                item_path = os.path.join(resolved_path, item)
                is_dir = os.path.isdir(item_path)
                
                has_files = False
                if is_dir:
                    try:
                        has_files = any(os.path.isfile(os.path.join(item_path, f)) 
                                      for f in os.listdir(item_path))
                    except:
                        pass
                
                items.append({
                    'name': item,
                    'path': item_path,
                    'type': 'directory' if is_dir else 'file',
                    'hasFiles': has_files
                })
        
        items.sort(key=lambda x: (x['type'] != 'directory', x['name']))
        can_go_up = resolved_path != WORKSPACE_ROOT
        
        return jsonify({
            'currentPath': resolved_path,
            'parentPath': os.path.dirname(resolved_path) if can_go_up else resolved_path,
            'items': items,
            'canGoUp': can_go_up
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/data/file', methods=['GET'])
def read_file():
    try:
        file_path = request.args.get('path')
        if not file_path:
            return jsonify({'error': 'File path is required'}), 400
        
        resolved_path = os.path.abspath(file_path)
        if not validate_path(resolved_path):
            return jsonify({'error': 'Access denied: path outside petrophysics-workplace'}), 403
        
        if not os.path.isfile(resolved_path):
            return jsonify({'error': 'Path is not a file'}), 400
        
        with open(resolved_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            json_content = json.loads(content)
            return jsonify({'content': json_content})
        except:
            return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': f'Failed to read file: {str(e)}'}), 500

# Well Management Routes
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api.route('/wells/preview-las', methods=['POST'])
def preview_las():
    """Preview LAS file content without saving"""
    try:
        data = request.get_json()
        las_content = data.get('lasContent')
        
        if not las_content:
            return jsonify({'error': 'LAS content is required'}), 400
        
        preview_info = LASProcessor.preview_las(las_content)
        return jsonify(preview_info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/wells/create-from-las', methods=['POST'])
def create_from_las():
    """Upload LAS file and create well in project"""
    try:
        if 'lasFile' not in request.files:
            return jsonify({'error': 'No LAS file provided'}), 400
        
        las_file = request.files['lasFile']
        project_path = request.form.get('projectPath')
        
        if not project_path:
            return jsonify({'error': 'Project path is required'}), 400
        
        if las_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(las_file.filename):
            return jsonify({'error': 'Invalid file type. Only .las files are allowed'}), 400
        
        resolved_project_path = os.path.abspath(project_path)
        if not validate_path(resolved_project_path):
            return jsonify({'error': 'Access denied: path outside petrophysics-workplace'}), 403
        
        if not os.path.exists(resolved_project_path):
            return jsonify({'error': 'Project path does not exist'}), 404
        
        filename = secure_filename(las_file.filename)
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.las', delete=False) as tmp_file:
            las_file.save(tmp_file.name)
            tmp_las_path = tmp_file.name
        
        try:
            well = LASProcessor.las_to_well(tmp_las_path)
            
            result = LASProcessor.save_well_to_project(
                well=well,
                project_path=resolved_project_path,
                las_source_file=tmp_las_path
            )
            
            return jsonify({
                'success': True,
                'message': f'Well "{well.well_name}" created successfully',
                'well': {
                    'id': well.well_name,
                    'name': well.well_name,
                    'type': well.well_type
                },
                'filePath': result['well_path'],
                'lasFilePath': result.get('las_path')
            }), 201
            
        finally:
            if os.path.exists(tmp_las_path):
                os.unlink(tmp_las_path)
                
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@api.route('/wells/list', methods=['GET'])
def list_wells():
    """List all wells in a project"""
    try:
        project_path = request.args.get('projectPath')
        
        if not project_path:
            return jsonify({'error': 'Project path is required'}), 400
        
        resolved_path = os.path.abspath(project_path)
        if not validate_path(resolved_path):
            return jsonify({'error': 'Access denied: path outside petrophysics-workplace'}), 403
        
        wells_folder = os.path.join(resolved_path, "10-WELLS")
        
        if not os.path.exists(wells_folder):
            return jsonify({'wells': []})
        
        wells = []
        for filename in os.listdir(wells_folder):
            if filename.endswith('.ptrc'):
                file_path = os.path.join(wells_folder, filename)
                try:
                    from utils.well_models import Well
                    well = Well.load(file_path)
                    wells.append({
                        'id': well.name,
                        'name': well.name,
                        'uwi': well.uwi,
                        'path': file_path,
                        'created_at': well.metadata.get('created_at'),
                        'source': well.metadata.get('source', 'manual')
                    })
                except Exception as e:
                    print(f"Error loading well {filename}: {e}")
                    continue
        
        wells.sort(key=lambda x: x['name'])
        return jsonify({'wells': wells})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
