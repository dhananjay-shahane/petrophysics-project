import os
import json
import tempfile
import traceback
import shutil
import lasio
import math
from pathlib import Path
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
from utils.project_utils import create_project_structure
from utils.fe_data_objects import Well, Dataset, Constant
from utils.LogPlot import LogPlotManager
from utils.logplotclass import create_multi_track_plot, FigureWidget

api = Blueprint('api', __name__)

WORKSPACE_ROOT = os.path.join(os.getcwd(), "petrophysics-workplace")
ALLOWED_EXTENSIONS = {'las', 'LAS'}

# Ensure workspace exists
Path(WORKSPACE_ROOT).mkdir(parents=True, exist_ok=True)

# Helper function to convert NaN to None for JSON serialization
def sanitize_value(value):
    """Convert NaN, Infinity, and other non-JSON values to None"""
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
    return value

def sanitize_list(lst):
    """Convert all NaN values in a list to None"""
    if not lst:
        return []
    return [sanitize_value(v) for v in lst]

# Get workspace info
@api.route('/workspace/info', methods=['GET'])
def get_workspace_info():
    return jsonify({
        'workspaceRoot': WORKSPACE_ROOT,
        'absolutePath': os.path.abspath(WORKSPACE_ROOT),
        'exists': os.path.exists(WORKSPACE_ROOT)
    })

# Helper function to validate paths (prevents symlink traversal)
def validate_path(path_str):
    try:
        # Normalize paths for cross-platform compatibility
        resolved = os.path.normpath(os.path.realpath(path_str))
        workspace = os.path.normpath(os.path.realpath(WORKSPACE_ROOT))
        # On Windows, also ensure paths are on the same drive
        if os.name == 'nt':
            # If paths are on different drives, path is invalid
            if os.path.splitdrive(resolved)[0].lower() != os.path.splitdrive(workspace)[0].lower():
                return False
        return resolved.startswith(workspace)
    except:
        return False

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
        
        # If the path doesn't exist or is not valid, use workspace root
        if not dir_path or not os.path.exists(dir_path):
            dir_path = WORKSPACE_ROOT
        
        resolved_path = os.path.abspath(dir_path)
        
        if not validate_path(resolved_path):
            # If validation fails, return workspace root instead of error
            resolved_path = os.path.abspath(WORKSPACE_ROOT)
        
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
        
        # If path doesn't exist, use workspace root
        if not os.path.exists(dir_path):
            dir_path = WORKSPACE_ROOT
        
        resolved_path = os.path.abspath(dir_path)
        if not validate_path(resolved_path):
            # Use workspace root as fallback
            resolved_path = os.path.abspath(WORKSPACE_ROOT)
        
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
        filename = data.get('filename', 'UNKNOWN')  # Get original filename if provided
        
        if not las_content:
            return jsonify({'error': 'LAS content is required'}), 400
        
        # Save content to temp file to parse with lasio
        with tempfile.NamedTemporaryFile(mode='w', suffix='.las', delete=False) as tmp_file:
            tmp_file.write(las_content)
            tmp_path = tmp_file.name
        
        try:
            las = lasio.read(tmp_path)
            
            # Extract well name - try multiple approaches
            well_name = None
            
            # Try WELL mnemonic first
            try:
                if hasattr(las.well, 'WELL'):
                    well_obj = las.well.WELL
                    if well_obj and well_obj.value:
                        well_name = str(well_obj.value).strip()
            except:
                pass
            
            # If not found, try accessing by iteration
            if not well_name:
                for item in las.well:
                    if item.mnemonic.upper() == 'WELL' and item.value:
                        well_name = str(item.value).strip()
                        break
            
            # If still not found, use original filename without extension
            if not well_name:
                well_name = Path(filename).stem if filename != 'UNKNOWN' else 'UNKNOWN'
            
            # Extract UWI
            uwi = ""
            try:
                if hasattr(las.well, 'UWI'):
                    uwi_obj = las.well.UWI
                    if uwi_obj and uwi_obj.value:
                        uwi = str(uwi_obj.value).strip()
            except:
                pass
            
            preview_info = {
                "wellName": well_name,
                "uwi": uwi,
                "company": str(las.well.COMP.value).strip() if hasattr(las.well, 'COMP') and las.well.COMP and las.well.COMP.value else "",
                "field": str(las.well.FLD.value).strip() if hasattr(las.well, 'FLD') and las.well.FLD and las.well.FLD.value else "",
                "location": str(las.well.LOC.value).strip() if hasattr(las.well, 'LOC') and las.well.LOC and las.well.LOC.value else "",
                "startDepth": float(las.well.STRT.value) if hasattr(las.well, 'STRT') and las.well.STRT and las.well.STRT.value is not None else None,
                "stopDepth": float(las.well.STOP.value) if hasattr(las.well, 'STOP') and las.well.STOP and las.well.STOP.value is not None else None,
                "step": float(las.well.STEP.value) if hasattr(las.well, 'STEP') and las.well.STEP and las.well.STEP.value is not None else None,
                "curveNames": [curve.mnemonic for curve in las.curves],
                "dataPoints": len(las.data) if las.data is not None else 0
            }
            
            return jsonify(preview_info)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/wells/create-from-las', methods=['POST'])
def create_from_las():
    """Upload LAS file and create well in project"""
    logs = []
    try:
        logs.append({'message': 'Starting LAS file upload...', 'type': 'info'})
        
        if 'lasFile' not in request.files:
            return jsonify({'error': 'No LAS file provided', 'logs': logs}), 400
        
        las_file = request.files['lasFile']
        project_path = request.form.get('projectPath')
        
        if not project_path:
            return jsonify({'error': 'Project path is required', 'logs': logs}), 400
        
        if las_file.filename == '':
            return jsonify({'error': 'No file selected', 'logs': logs}), 400
        
        logs.append({'message': f'File selected: {las_file.filename}', 'type': 'info'})
        
        if not allowed_file(las_file.filename):
            logs.append({'message': 'ERROR: Invalid file type. Only .las files are allowed', 'type': 'error'})
            return jsonify({'error': 'Invalid file type. Only .las files are allowed', 'logs': logs}), 400
        
        resolved_project_path = os.path.abspath(project_path)
        if not validate_path(resolved_project_path):
            logs.append({'message': 'ERROR: Access denied - path outside workspace', 'type': 'error'})
            return jsonify({'error': 'Access denied: path outside petrophysics-workplace', 'logs': logs}), 403
        
        if not os.path.exists(resolved_project_path):
            logs.append({'message': 'ERROR: Project path does not exist', 'type': 'error'})
            return jsonify({'error': 'Project path does not exist', 'logs': logs}), 404
        
        filename = secure_filename(las_file.filename)
        logs.append({'message': f'Saving file as: {filename}', 'type': 'info'})
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.las', delete=False) as tmp_file:
            las_file.save(tmp_file.name)
            tmp_las_path = tmp_file.name
        
        try:
            logs.append({'message': 'Parsing LAS file...', 'type': 'info'})
            
            # Read LAS file to get well information
            las = lasio.read(tmp_las_path)
            
            # Extract well name - try multiple approaches
            well_name = None
            
            # Try WELL mnemonic first
            try:
                if hasattr(las.well, 'WELL'):
                    well_obj = las.well.WELL
                    if well_obj and well_obj.value:
                        well_name = str(well_obj.value).strip()
            except:
                pass
            
            # If not found, try accessing by iteration
            if not well_name:
                for item in las.well:
                    if item.mnemonic.upper() == 'WELL' and item.value:
                        well_name = str(item.value).strip()
                        break
            
            # If still not found, use original filename without extension
            if not well_name:
                well_name = Path(filename).stem
            
            logs.append({'message': f'Extracted well name: {well_name}', 'type': 'info'})
            
            # Extract dataset name from params.SET if available
            dataset_name = 'MAIN'
            try:
                if hasattr(las.params, 'SET') and las.params.SET.value:
                    dataset_name = str(las.params.SET.value).strip()
            except:
                pass
            
            logs.append({'message': f'Dataset name: {dataset_name}', 'type': 'info'})
            
            # Get top and bottom depths
            top = las.well.STRT.value
            bottom = las.well.STOP.value
            
            # Create dataset from LAS file using Dataset.from_las
            dataset = Dataset.from_las(
                filename=tmp_las_path,
                dataset_name=dataset_name,
                dataset_type='Cont',
                well_name=well_name
            )
            
            logs.append({'message': 'LAS file parsed successfully', 'type': 'success'})
            logs.append({'message': f'Found {len(dataset.well_logs)} log curves', 'type': 'info'})
            
            # Check if well already exists
            wells_folder = os.path.join(resolved_project_path, '10-WELLS')
            os.makedirs(wells_folder, exist_ok=True)
            
            well_file_path = os.path.join(wells_folder, f'{well_name}.ptrc')
            
            if os.path.exists(well_file_path):
                # Load existing well and check for duplicate dataset
                logs.append({'message': f'Well "{well_name}" already exists, checking for duplicates...', 'type': 'info'})
                well = Well.deserialize(filepath=well_file_path)
                
                # Check if dataset with same name already exists
                existing_dataset_names = [dtst.name for dtst in well.datasets]
                if dataset_name in existing_dataset_names:
                    logs.append({'message': f'WARNING: Dataset "{dataset_name}" already exists in well "{well_name}"', 'type': 'warning'})
                    logs.append({'message': 'Upload cancelled to prevent duplicate data', 'type': 'error'})
                    return jsonify({
                        'error': f'Dataset "{dataset_name}" already exists in well "{well_name}". Cannot upload duplicate data.',
                        'logs': logs
                    }), 400
                
                # Append new dataset
                well.datasets.append(dataset)
                logs.append({'message': f'Dataset "{dataset_name}" appended to existing well', 'type': 'success'})
            else:
                # Create new well with REFERENCE and WELL_HEADER datasets
                logs.append({'message': f'Creating new well "{well_name}"...', 'type': 'info'})
                well = Well(
                    date_created=datetime.now(),
                    well_name=well_name,
                    well_type='Dev'
                )
                
                # Create REFERENCE dataset
                ref = Dataset.reference(
                    top=0,
                    bottom=bottom,
                    dataset_name='REFERENCE',
                    dataset_type='REFERENCE',
                    well_name=well_name
                )
                
                # Create WELL_HEADER dataset
                wh = Dataset.well_header(
                    dataset_name='WELL_HEADER',
                    dataset_type='WELL_HEADER',
                    well_name=well_name
                )
                const = Constant(name='WELL_NAME', value=well.well_name, tag=well.well_name)
                wh.constants.append(const)
                
                # Add datasets to well
                well.datasets.append(ref)
                well.datasets.append(wh)
                well.datasets.append(dataset)
                
                logs.append({'message': f'New well created with REFERENCE and WELL_HEADER datasets', 'type': 'success'})
            
            logs.append({'message': 'Saving well to project...', 'type': 'info'})
            
            # Save well to .ptrc file
            well.serialize(filename=well_file_path)
            
            logs.append({'message': f'SUCCESS: Well saved to: {well_file_path}', 'type': 'success'})
            
            # Copy LAS file to 02-INPUT_LAS_FOLDER
            las_folder = os.path.join(resolved_project_path, '02-INPUT_LAS_FOLDER')
            os.makedirs(las_folder, exist_ok=True)
            las_destination = os.path.join(las_folder, filename)
            shutil.copy2(tmp_las_path, las_destination)
            
            logs.append({'message': f'SUCCESS: LAS file copied to: {las_destination}', 'type': 'success'})
            logs.append({'message': f'Well "{well_name}" created successfully!', 'type': 'success'})
            
            return jsonify({
                'success': True,
                'message': f'Well "{well_name}" created successfully',
                'well': {
                    'id': well_name,
                    'name': well_name,
                    'type': well.well_type
                },
                'filePath': well_file_path,
                'lasFilePath': las_destination,
                'logs': logs
            }), 201
            
        finally:
            if os.path.exists(tmp_las_path):
                os.unlink(tmp_las_path)
                
    except Exception as e:
        traceback.print_exc()
        logs.append({'message': f'ERROR: {str(e)}', 'type': 'error'})
        return jsonify({'error': str(e), 'logs': logs}), 500

@api.route('/wells/load', methods=['GET'])
def load_well():
    """Load well data from .ptrc file"""
    try:
        file_path = request.args.get('filePath')
        
        if not file_path:
            return jsonify({'error': 'File path is required'}), 400
        
        resolved_path = os.path.abspath(file_path)
        if not validate_path(resolved_path):
            return jsonify({'error': 'Access denied: path outside petrophysics-workplace'}), 403
        
        if not os.path.exists(resolved_path):
            return jsonify({'error': 'Well file not found'}), 404
        
        if not resolved_path.endswith('.ptrc'):
            return jsonify({'error': 'Invalid file type. Only .ptrc files are supported'}), 400
        
        # Load well using Well.deserialize
        well = Well.deserialize(filepath=resolved_path)
        
        # Format datasets for frontend
        datasets = []
        for dataset in well.datasets:
            # Format well logs
            logs = []
            for log in dataset.well_logs:
                preview_values = log.log[:100] if hasattr(log, 'log') else []
                logs.append({
                    'name': log.name,
                    'date': str(log.date) if hasattr(log, 'date') else '',
                    'description': log.description if hasattr(log, 'description') else '',
                    'dataset': log.dtst if hasattr(log, 'dtst') else dataset.name,
                    'interpolation': log.interpolation if hasattr(log, 'interpolation') else '',
                    'logType': log.log_type if hasattr(log, 'log_type') else '',
                    'values': sanitize_list(preview_values)  # Limit to first 100 values for preview, sanitize NaN
                })
            
            # Format constants
            constants = []
            if hasattr(dataset, 'constants') and dataset.constants:
                for const in dataset.constants:
                    constants.append({
                        'name': const.name if hasattr(const, 'name') else '',
                        'value': str(const.value) if hasattr(const, 'value') else '',
                        'tag': const.tag if hasattr(const, 'tag') else ''
                    })
            
            datasets.append({
                'name': dataset.name,
                'type': dataset.type,
                'wellname': dataset.wellname,
                'indexName': dataset.index_name if hasattr(dataset, 'index_name') else 'DEPTH',
                'logs': logs,
                'constants': constants
            })
        
        return jsonify({
            'success': True,
            'well': {
                'name': well.well_name,
                'type': well.well_type,
                'dateCreated': str(well.date_created) if hasattr(well, 'date_created') else '',
                'datasets': datasets
            }
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@api.route('/wells/data', methods=['GET'])
def get_well_data():
    """Get complete well dataset data for data browser"""
    try:
        well_path = request.args.get('wellPath')
        
        if not well_path:
            return jsonify({'error': 'Well path is required'}), 400
        
        resolved_path = os.path.abspath(well_path)
        if not validate_path(resolved_path):
            return jsonify({'error': 'Access denied: path outside petrophysics-workplace'}), 403
        
        if not os.path.exists(resolved_path):
            return jsonify({'error': 'Well file not found'}), 404
        
        # Load well using Well.deserialize
        well = Well.deserialize(filepath=resolved_path)
        
        # Format datasets with complete data
        datasets = []
        for dataset in well.datasets:
            # Format well logs with all values
            logs = []
            for log in dataset.well_logs:
                logs.append({
                    'name': log.name,
                    'date': str(log.date) if hasattr(log, 'date') else '',
                    'description': log.description if hasattr(log, 'description') else '',
                    'dtst': log.dtst if hasattr(log, 'dtst') else dataset.name,
                    'interpolation': log.interpolation if hasattr(log, 'interpolation') else '',
                    'log_type': log.log_type if hasattr(log, 'log_type') else '',
                    'log': sanitize_list(log.log) if hasattr(log, 'log') else []  # Complete values with NaN converted to null
                })
            
            # Format constants
            constants = []
            if hasattr(dataset, 'constants') and dataset.constants:
                for const in dataset.constants:
                    constants.append({
                        'name': const.name if hasattr(const, 'name') else '',
                        'value': const.value if hasattr(const, 'value') else '',
                        'tag': const.tag if hasattr(const, 'tag') else ''
                    })
            
            datasets.append({
                'name': dataset.name,
                'type': dataset.type,
                'wellname': dataset.wellname,
                'index_name': dataset.index_name if hasattr(dataset, 'index_name') else 'DEPTH',
                'index_log': sanitize_list(dataset.index_log) if hasattr(dataset, 'index_log') else [],
                'well_logs': logs,
                'constants': constants
            })
        
        return jsonify({
            'success': True,
            'datasets': datasets
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@api.route('/wells/dataset-details', methods=['GET'])
def get_dataset_details():
    """Get specific dataset details for data browser"""
    try:
        well_path = request.args.get('wellPath')
        dataset_name = request.args.get('datasetName')
        
        if not well_path:
            return jsonify({'error': 'Well path is required'}), 400
        
        if not dataset_name:
            return jsonify({'error': 'Dataset name is required'}), 400
        
        resolved_path = os.path.abspath(well_path)
        if not validate_path(resolved_path):
            return jsonify({'error': 'Access denied: path outside petrophysics-workplace'}), 403
        
        if not os.path.exists(resolved_path):
            return jsonify({'error': 'Well file not found'}), 404
        
        # Load well using Well.deserialize
        well = Well.deserialize(filepath=resolved_path)
        
        # Find the requested dataset
        target_dataset = None
        for dataset in well.datasets:
            if dataset.name == dataset_name:
                target_dataset = dataset
                break
        
        if not target_dataset:
            return jsonify({'error': f'Dataset "{dataset_name}" not found'}), 404
        
        # Format well logs with complete data
        logs = []
        for log in target_dataset.well_logs:
            logs.append({
                'name': log.name,
                'date': str(log.date) if hasattr(log, 'date') else '',
                'description': log.description if hasattr(log, 'description') else '',
                'dtst': log.dtst if hasattr(log, 'dtst') else target_dataset.name,
                'interpolation': log.interpolation if hasattr(log, 'interpolation') else '',
                'log_type': log.log_type if hasattr(log, 'log_type') else '',
                'log': sanitize_list(log.log) if hasattr(log, 'log') else []
            })
        
        # Format constants
        constants = []
        if hasattr(target_dataset, 'constants') and target_dataset.constants:
            for const in target_dataset.constants:
                constants.append({
                    'name': const.name if hasattr(const, 'name') else '',
                    'value': const.value if hasattr(const, 'value') else '',
                    'tag': const.tag if hasattr(const, 'tag') else ''
                })
        
        dataset_details = {
            'name': target_dataset.name,
            'type': target_dataset.type,
            'wellname': target_dataset.wellname,
            'index_name': target_dataset.index_name if hasattr(target_dataset, 'index_name') else 'DEPTH',
            'index_log': sanitize_list(target_dataset.index_log) if hasattr(target_dataset, 'index_log') else [],
            'well_logs': logs,
            'constants': constants
        }
        
        return jsonify({
            'success': True,
            'dataset': dataset_details
        }), 200
        
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
                    well = Well.deserialize(filepath=file_path)
                    wells.append({
                        'id': well.well_name,
                        'name': well.well_name,
                        'type': well.well_type,
                        'path': file_path,
                        'created_at': well.date_created.isoformat() if well.date_created else None,
                        'datasets': len(well.datasets)
                    })
                except Exception as e:
                    print(f"Error loading well {filename}: {e}")
                    continue
        
        wells.sort(key=lambda x: x['name'])
        return jsonify({'wells': wells})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Session Management Routes
@api.route('/session/project', methods=['POST'])
def save_project_session():
    """Save current project path to session"""
    try:
        data = request.get_json()
        project_path = data.get('projectPath')
        project_name = data.get('projectName')
        created_at = data.get('createdAt')
        
        if not project_path:
            return jsonify({'error': 'Project path is required'}), 400
        
        # Validate path
        resolved_path = os.path.abspath(project_path)
        if not validate_path(resolved_path):
            return jsonify({'error': 'Access denied: path outside petrophysics-workplace'}), 403
        
        # Store in session
        session['project_path'] = project_path
        session['project_name'] = project_name
        session['created_at'] = created_at
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'Project saved to session',
            'projectPath': project_path,
            'projectName': project_name
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/session/project', methods=['GET'])
def get_project_session():
    """Get current project path from session"""
    try:
        project_path = session.get('project_path')
        project_name = session.get('project_name')
        created_at = session.get('created_at')
        
        if not project_path:
            return jsonify({
                'success': True,
                'hasProject': False,
                'projectPath': None,
                'projectName': None,
                'createdAt': None
            }), 200
        
        return jsonify({
            'success': True,
            'hasProject': True,
            'projectPath': project_path,
            'projectName': project_name,
            'createdAt': created_at
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/session/clear', methods=['POST'])
def clear_session():
    """Clear the session"""
    try:
        session.clear()
        return jsonify({
            'success': True,
            'message': 'Session cleared'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Well Datasets Route
@api.route('/wells/datasets', methods=['GET'])
def get_well_datasets():
    """Get all datasets for a well"""
    try:
        project_path = request.args.get('projectPath')
        well_name = request.args.get('wellName')
        
        if not project_path or not well_name:
            return jsonify({'error': 'Project path and well name are required'}), 400
        
        # Validate path
        resolved_path = os.path.abspath(project_path)
        if not validate_path(resolved_path):
            return jsonify({'error': 'Access denied: path outside petrophysics-workplace'}), 403
        
        # Load the well
        wells_folder = os.path.join(resolved_path, "10-WELLS")
        well_file = os.path.join(wells_folder, f"{well_name}.ptrc")
        
        if not os.path.exists(well_file):
            return jsonify({'error': f'Well {well_name} not found'}), 404
        
        well = Well.deserialize(filepath=well_file)
        
        # Collect all unique log names from datasets
        datasets = []
        seen_logs = set()
        
        for dataset in well.datasets:
            # Add dataset info
            datasets.append({
                'name': dataset.name,
                'type': dataset.type,
                'date_created': dataset.date_created.isoformat() if dataset.date_created else None
            })
            
            # Also collect individual well logs
            for well_log in dataset.well_logs:
                if well_log.name not in seen_logs:
                    seen_logs.add(well_log.name)
                    datasets.append({
                        'name': well_log.name,
                        'type': 'continuous' if well_log.log_type == 'continuous' else dataset.type,
                        'description': well_log.description
                    })
        
        return jsonify({
            'success': True,
            'wellName': well.well_name,
            'datasets': datasets
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Well Log Plotting Routes
@api.route('/wells/<well_id>/log-plot', methods=['POST'])
def generate_log_plot(well_id):
    """Generate a well log plot for specified logs"""
    try:
        print(f"[LOG PLOT] Starting log plot generation for well: {well_id}")
        data = request.get_json()
        project_path = data.get('projectPath')
        log_names = data.get('logNames', [])
        
        if not project_path:
            print("[LOG PLOT] Error: Project path is required")
            return jsonify({'error': 'Project path is required'}), 400
        
        if not log_names or len(log_names) == 0:
            print("[LOG PLOT] Error: No log names provided")
            return jsonify({'error': 'At least one log name is required'}), 400
        
        print(f"[LOG PLOT] Plotting logs: {', '.join(log_names)}")
        
        # Validate path
        resolved_path = os.path.abspath(project_path)
        if not validate_path(resolved_path):
            print("[LOG PLOT] Error: Path validation failed")
            return jsonify({'error': 'Access denied: path outside petrophysics-workplace'}), 403
        
        # Load the well
        wells_folder = os.path.join(resolved_path, "10-WELLS")
        well_file = os.path.join(wells_folder, f"{well_id}.ptrc")
        
        print(f"[LOG PLOT] Loading well from: {well_file}")
        if not os.path.exists(well_file):
            print(f"[LOG PLOT] Error: Well file not found")
            return jsonify({'error': f'Well {well_id} not found'}), 404
        
        well = Well.deserialize(filepath=well_file)
        print(f"[LOG PLOT] Well loaded successfully: {well.well_name}")
        print(f"[LOG PLOT] Number of datasets: {len(well.datasets)}")
        
        # Generate the plot using GitHub repo classes
        print("[LOG PLOT] Initializing LogPlotManager...")
        plot_manager = LogPlotManager()
        
        print("[LOG PLOT] Creating log plot with matplotlib...")
        plot_image = plot_manager.create_log_plot(well, log_names)
        
        if not plot_image:
            print("[LOG PLOT] Error: Plot generation failed")
            return jsonify({'error': 'Failed to generate plot'}), 500
        
        print("[LOG PLOT] Plot generated successfully!")
        print(f"[LOG PLOT] Image size: {len(plot_image)} characters (base64)")
        
        return jsonify({
            'success': True,
            'image': plot_image,
            'format': 'png',
            'encoding': 'base64',
            'logs': [
                f"Starting log plot generation for well: {well_id}",
                f"Plotting logs: {', '.join(log_names)}",
                f"Well loaded: {well.well_name}",
                f"Number of datasets: {len(well.datasets)}",
                "Plot generated successfully!"
            ]
        }), 200
        
    except Exception as e:
        print(f"[LOG PLOT] Error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@api.route('/wells/<well_id>/cross-plot', methods=['POST'])
def generate_cross_plot(well_id):
    """Generate a cross plot of two logs"""
    try:
        print(f"[CROSS PLOT] Starting cross plot generation for well: {well_id}")
        data = request.get_json()
        project_path = data.get('projectPath')
        x_log_name = data.get('xLog')
        y_log_name = data.get('yLog')
        
        if not project_path or not x_log_name or not y_log_name:
            print("[CROSS PLOT] Error: Missing required parameters")
            return jsonify({'error': 'Project path, x log, and y log are required'}), 400
        
        print(f"[CROSS PLOT] X-axis log: {x_log_name}")
        print(f"[CROSS PLOT] Y-axis log: {y_log_name}")
        
        # Validate path
        resolved_path = os.path.abspath(project_path)
        if not validate_path(resolved_path):
            print("[CROSS PLOT] Error: Path validation failed")
            return jsonify({'error': 'Access denied: path outside petrophysics-workplace'}), 403
        
        # Load the well
        wells_folder = os.path.join(resolved_path, "10-WELLS")
        well_file = os.path.join(wells_folder, f"{well_id}.ptrc")
        
        print(f"[CROSS PLOT] Loading well from: {well_file}")
        if not os.path.exists(well_file):
            print("[CROSS PLOT] Error: Well file not found")
            return jsonify({'error': f'Well {well_id} not found'}), 404
        
        well = Well.deserialize(filepath=well_file)
        print(f"[CROSS PLOT] Well loaded successfully: {well.well_name}")
        print(f"[CROSS PLOT] Number of datasets: {len(well.datasets)}")
        
        # Use CPI.py CrossPlotManager (GitHub repo pattern)
        from utils.CPI import CrossPlotManager
        
        print("[CROSS PLOT] Initializing CrossPlotManager...")
        manager = CrossPlotManager()
        
        print("[CROSS PLOT] Creating cross plot with matplotlib...")
        plot_image = manager.create_cross_plot(well, x_log_name, y_log_name)
        
        if plot_image is None:
            print("[CROSS PLOT] Error: Failed to generate plot")
            return jsonify({'error': 'Failed to generate cross plot - logs not found or no valid data'}), 404
        
        print("[CROSS PLOT] Cross plot generated successfully!")
        print(f"[CROSS PLOT] Image size: {len(plot_image)} characters (base64)")
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{plot_image}',
            'format': 'png',
            'encoding': 'base64',
            'logs': [
                f"Starting cross plot generation for well: {well_id}",
                f"X-axis log: {x_log_name}",
                f"Y-axis log: {y_log_name}",
                f"Well loaded: {well.well_name}",
                f"Number of datasets: {len(well.datasets)}",
                "Cross plot generated successfully!"
            ]
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
