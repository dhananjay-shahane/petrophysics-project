from flask import Blueprint, request, jsonify
import os

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/create', methods=['POST'])
def create_project():
    try:
        data = request.json
        name = data.get('name')
        custom_path = data.get('path')
        
        if not name or not name.strip():
            return jsonify({"error": "Project name is required"}), 400
        
        if not custom_path or not custom_path.strip():
            return jsonify({"error": "Project path is required"}), 400
        
        project_name = name.strip()
        project_base_path = custom_path.strip()
        
        # Validate project name
        if not project_name.replace('-', '').replace('_', '').isalnum():
            return jsonify({"error": "Project name can only contain letters, numbers, hyphens, and underscores"}), 400
        
        base_dir = os.path.join(project_base_path, project_name)
        
        # Create project folders
        folders = [
            "01-OUTPUT",
            "02-INPUT_LAS_FOLDER",
            "03-DEVIATION",
            "04-WELL_HEADER",
            "05-TOPS_FOLDER",
            "06-ZONES_FOLDER",
            "07-DATA_EXPORTS",
            "08-VOL_MODELS",
            "09-SPECS",
            "10-WELLS"
        ]
        
        os.makedirs(base_dir, exist_ok=True)
        
        for folder in folders:
            os.makedirs(os.path.join(base_dir, folder), exist_ok=True)
        
        return jsonify({
            "success": True,
            "message": f"Project '{project_name}' created successfully",
            "path": base_dir,
            "folders": folders
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@projects_bp.route('/list', methods=['GET'])
def list_projects():
    try:
        database_dir = os.path.join(os.getcwd(), "database")
        
        if not os.path.exists(database_dir):
            os.makedirs(database_dir, exist_ok=True)
            return jsonify({"success": True, "projects": []})
        
        files = os.listdir(database_dir)
        json_files = [f for f in files if f.endswith('.json')]
        
        projects = []
        for file in json_files:
            try:
                import json
                file_path = os.path.join(database_dir, file)
                stats = os.stat(file_path)
                with open(file_path, 'r') as f:
                    project_data = json.load(f)
                projects.append({
                    "fileName": file,
                    "name": project_data.get("name"),
                    "path": project_data.get("path"),
                    "wellCount": len(project_data.get("wells", [])),
                    "createdAt": project_data.get("createdAt"),
                    "updatedAt": project_data.get("updatedAt", stats.st_mtime)
                })
            except:
                continue
        
        return jsonify({"success": True, "projects": projects})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
