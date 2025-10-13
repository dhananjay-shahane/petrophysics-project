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
        
        # Use default workspace if no project path provided
        if not project_path or not project_path.strip() or project_path == "No path selected":
            project_path = os.path.join(os.getcwd(), "petrophysics-workplace")
        
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
                
                # Extract logs from the continuous dataset
                logs = []
                datasets = well_data.get('datasets', [])
                for ds in datasets:
                    if ds.get('type') in ['Cont', 'LOG_DATA', 'Continuous']:
                        well_logs = ds.get('well_logs', [])
                        logs = [log.get('name') for log in well_logs]
                        break
                
                wells.append({
                    "id": well_data.get('id', file.replace('.json', '')),
                    "name": well_data.get('well_name', file.replace('.json', '')),
                    "well_name": well_data.get('well_name', file.replace('.json', '')),
                    "path": file_path,
                    "logs": logs,
                    "metadata": well_data.get('metadata', {}),
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

@wells_bp.route('/<well_name>/log-plot', methods=['GET'])
def get_log_plot_data(well_name):
    """Get well log plot data for visualization"""
    try:
        # Accept projectPath from query params, default to workspace root
        project_path = request.args.get('projectPath')
        if not project_path or not project_path.strip() or project_path == "No path selected":
            project_path = os.path.join(os.getcwd(), 'petrophysics-workplace')
        
        # Security: Validate project path is within workspace using commonpath
        workspace_root = os.path.join(os.getcwd(), 'petrophysics-workplace')
        resolved_workspace = os.path.realpath(workspace_root)
        resolved_project_path = os.path.realpath(project_path)
        
        try:
            common = os.path.commonpath([resolved_workspace, resolved_project_path])
            if common != resolved_workspace:
                return jsonify({"error": "Access denied: project path outside workspace"}), 403
        except ValueError:
            return jsonify({"error": "Access denied: invalid project path"}), 403
        
        wells_folder = os.path.join(resolved_project_path, '10-WELLS')
        well_path = os.path.join(wells_folder, f"{well_name}.json")
        
        if not os.path.exists(well_path):
            return jsonify({"error": "Well not found"}), 404
        
        with open(well_path, 'r') as f:
            well_data = json.load(f)
        
        # Check if well has new format (datasets) or old format (flat data array)
        datasets = well_data.get('datasets', [])
        flat_data = well_data.get('data', [])
        
        tracks = []
        index_name = 'DEPT'
        
        if datasets:
            # New format: Find the first continuous dataset
            log_dataset = None
            for ds in datasets:
                if ds.get('type') in ['Cont', 'LOG_DATA', 'Continuous']:
                    log_dataset = ds
                    break
            
            if not log_dataset:
                return jsonify({"error": "No log dataset found"}), 404
            
            # Format data for frontend
            index_log = log_dataset.get('index_log', [])
            index_name = log_dataset.get('index_name', 'DEPT')
            well_logs = log_dataset.get('well_logs', [])
            
            for log in well_logs[:6]:  # Limit to 6 tracks
                tracks.append({
                    'name': log.get('name'),
                    'unit': log.get('unit', ''),
                    'data': log.get('log', []),
                    'indexLog': index_log,
                    'indexName': index_name
                })
        
        elif flat_data:
            # Old format: Convert flat data array to tracks
            if len(flat_data) > 0:
                # Get all column names except DEPT
                columns = [k for k in flat_data[0].keys() if k != 'DEPT']
                depth_values = [row.get('DEPT') for row in flat_data]
                
                for col in columns[:6]:  # Limit to 6 tracks
                    log_values = [row.get(col) for row in flat_data]
                    tracks.append({
                        'name': col,
                        'unit': '',
                        'data': log_values,
                        'indexLog': depth_values,
                        'indexName': 'DEPT'
                    })
        else:
            return jsonify({"error": "No log data found in well"}), 404
        
        return jsonify({
            'wellName': well_data.get('well_name', well_name),
            'tracks': tracks,
            'indexName': index_name
        })
    
    except Exception as e:
        import traceback
        print(f"Error in log-plot endpoint: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@wells_bp.route('/<well_name>/cross-plot', methods=['POST'])
def get_cross_plot_data(well_name):
    """Generate cross plot data"""
    try:
        data = request.json
        x_curve = data.get('xCurve')
        y_curve = data.get('yCurve')
        color_curve = data.get('colorCurve')
        project_path = data.get('projectPath')
        
        if not x_curve or not y_curve:
            return jsonify({"error": "xCurve and yCurve are required"}), 400
        
        # Default to workspace root if no project path provided
        if not project_path or not project_path.strip() or project_path == "No path selected":
            project_path = os.path.join(os.getcwd(), 'petrophysics-workplace')
        
        # Security: Validate project path is within workspace using commonpath
        workspace_root = os.path.join(os.getcwd(), 'petrophysics-workplace')
        resolved_workspace = os.path.realpath(workspace_root)
        resolved_project_path = os.path.realpath(project_path)
        
        try:
            common = os.path.commonpath([resolved_workspace, resolved_project_path])
            if common != resolved_workspace:
                return jsonify({"error": "Access denied: project path outside workspace"}), 403
        except ValueError:
            return jsonify({"error": "Access denied: invalid project path"}), 403
        
        wells_folder = os.path.join(resolved_project_path, '10-WELLS')
        well_path = os.path.join(wells_folder, f"{well_name}.json")
        
        if not os.path.exists(well_path):
            return jsonify({"error": "Well not found"}), 404
        
        with open(well_path, 'r') as f:
            well_data = json.load(f)
        
        # Find the continuous dataset
        datasets = well_data.get('datasets', [])
        log_dataset = None
        
        for ds in datasets:
            if ds.get('type') in ['Cont', 'LOG_DATA', 'Continuous']:
                log_dataset = ds
                break
        
        if not log_dataset:
            return jsonify({"error": "No log dataset found"}), 404
        
        # Get the log data
        well_logs = log_dataset.get('well_logs', [])
        x_log = None
        y_log = None
        color_log = None
        
        for log in well_logs:
            if log.get('name') == x_curve:
                x_log = log.get('log', [])
            if log.get('name') == y_curve:
                y_log = log.get('log', [])
            if color_curve and log.get('name') == color_curve:
                color_log = log.get('log', [])
        
        if x_log is None or y_log is None:
            return jsonify({"error": "Curves not found"}), 404
        
        # Filter valid data points
        data_points = []
        for i in range(min(len(x_log), len(y_log))):
            x_val = x_log[i]
            y_val = y_log[i]
            
            if x_val is not None and y_val is not None and x_val != -999.25 and y_val != -999.25:
                point = {'x': x_val, 'y': y_val}
                if color_log and i < len(color_log) and color_log[i] is not None:
                    point['color'] = color_log[i]
                data_points.append(point)
        
        # Calculate correlation if we have data
        correlation = 0
        if len(data_points) > 1:
            import numpy as np
            x_vals = [p['x'] for p in data_points]
            y_vals = [p['y'] for p in data_points]
            correlation = np.corrcoef(x_vals, y_vals)[0, 1]
        
        return jsonify({
            'data': data_points,
            'correlation': float(correlation) if not np.isnan(correlation) else 0,
            'xCurve': x_curve,
            'yCurve': y_curve,
            'colorCurve': color_curve
        })
    
    except Exception as e:
        import traceback
        print(f"Error in cross-plot endpoint: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500
