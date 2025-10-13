from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
from ..utils.las_processor import WellManager

wells_bp = Blueprint('wells', __name__)

@wells_bp.route('/list', methods=['GET'])
def list_wells():
    try:
        project_path = request.args.get('projectPath')
        
        if not project_path or not project_path.strip():
            return jsonify({"error": "Project path is required"}), 400
        
        # Security: Validate project path is within workspace
        workspace_root = os.path.join(os.getcwd(), "petrophysics-workplace")
        resolved_project_path = os.path.realpath(project_path)
        
        if not resolved_project_path.startswith(os.path.realpath(workspace_root)):
            return jsonify({"error": "Access denied: project path outside workspace"}), 403
        
        wells_dir = os.path.join(resolved_project_path, "10-WELLS")
        
        if not os.path.exists(wells_dir):
            return jsonify({"success": True, "wells": []})
        
        files = os.listdir(wells_dir)
        json_files = [f for f in files if f.endswith('.json')]
        
        wells = []
        for file in json_files:
            try:
                file_path = os.path.join(wells_dir, file)
                with open(file_path, 'r') as f:
                    well_data = json.load(f)
                wells.append({
                    "id": well_data.get('id', file.replace('.json', '')),
                    "name": well_data.get('well_name', file.replace('.json', '')),
                    "path": file_path,
                    "data": well_data
                })
            except Exception as e:
                print(f"Error reading well file {file}: {e}")
                continue
        
        return jsonify({"success": True, "wells": wells})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wells_bp.route('/upload-las', methods=['POST'])
def upload_las():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.endswith('.las'):
            return jsonify({"error": "File must be a .las file"}), 400
        
        # Get project path from form data or use default
        project_path = request.form.get('projectPath', os.path.join(os.getcwd(), 'petrophysics-workplace'))
        
        # Security check
        workspace_root = os.path.join(os.getcwd(), "petrophysics-workplace")
        if not os.path.realpath(project_path).startswith(os.path.realpath(workspace_root)):
            project_path = workspace_root
        
        temp_folder = os.path.join(project_path, '02-INPUT_LAS_FOLDER')
        os.makedirs(temp_folder, exist_ok=True)
        
        filename = secure_filename(file.filename)
        las_path = os.path.join(temp_folder, filename)
        file.save(las_path)
        
        # Process LAS file
        well_manager = WellManager(project_path)
        well = well_manager.create_well_from_las(las_path, well_type='Dev')
        
        return jsonify({
            "success": True,
            "message": f"Well '{well.well_name}' created/updated successfully",
            "well": well.to_dict()
        })
    
    except Exception as e:
        import traceback
        print(f"Error uploading LAS file: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@wells_bp.route('/<well_name>', methods=['GET'])
def get_well(well_name):
    try:
        project_path = request.args.get('projectPath', os.path.join(os.getcwd(), 'petrophysics-workplace'))
        
        well_manager = WellManager(project_path)
        well = well_manager.get_well_by_name(well_name)
        
        if well:
            return jsonify(well.to_dict())
        
        return jsonify({"error": "Well not found"}), 404
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@wells_bp.route('/', methods=['GET'])
def get_all_wells():
    try:
        project_path = request.args.get('projectPath', os.path.join(os.getcwd(), 'petrophysics-workplace'))
        
        well_manager = WellManager(project_path)
        wells = well_manager.load_wells()
        
        return jsonify([well.to_dict() for well in wells])
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
