from flask import Blueprint, request, jsonify, send_file
import os
import json
from ..utils.plot_generator import PlotGenerator
from ..utils.las_processor import WellManager

visualization_bp = Blueprint('visualization', __name__)

@visualization_bp.route('/well-log-plot', methods=['POST'])
def generate_well_log_plot():
    try:
        data = request.json
        well_name = data.get('wellName')
        dataset_name = data.get('datasetName')
        log_names = data.get('logNames', [])
        project_path = data.get('projectPath', os.path.join(os.getcwd(), 'petrophysics-workplace'))
        
        if not well_name or not dataset_name or not log_names:
            return jsonify({"error": "wellName, datasetName, and logNames are required"}), 400
        
        # Load well data
        well_manager = WellManager(project_path)
        well = well_manager.get_well_by_name(well_name)
        
        if not well:
            return jsonify({"error": "Well not found"}), 404
        
        # Generate plot
        output_dir = os.path.join(os.getcwd(), 'public', 'well-plots')
        os.makedirs(output_dir, exist_ok=True)
        
        import time
        filename = f"well-log-{int(time.time() * 1000)}.png"
        output_path = os.path.join(output_dir, filename)
        
        PlotGenerator.generate_well_log_plot(
            well_data=well.to_dict(),
            dataset_name=dataset_name,
            log_names=log_names,
            output_path=output_path
        )
        
        return jsonify({
            "success": True,
            "plotUrl": f"/well-plots/{filename}",
            "message": "Well log plot generated successfully"
        })
    
    except Exception as e:
        import traceback
        print(f"Error generating well log plot: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@visualization_bp.route('/cross-plot', methods=['POST'])
def generate_cross_plot():
    try:
        data = request.json
        well_name = data.get('wellName')
        dataset_name = data.get('datasetName')
        x_log = data.get('xLog')
        y_log = data.get('yLog')
        project_path = data.get('projectPath', os.path.join(os.getcwd(), 'petrophysics-workplace'))
        
        if not well_name or not dataset_name or not x_log or not y_log:
            return jsonify({"error": "wellName, datasetName, xLog, and yLog are required"}), 400
        
        # Load well data
        well_manager = WellManager(project_path)
        well = well_manager.get_well_by_name(well_name)
        
        if not well:
            return jsonify({"error": "Well not found"}), 404
        
        # Generate plot
        output_dir = os.path.join(os.getcwd(), 'public', 'well-plots')
        os.makedirs(output_dir, exist_ok=True)
        
        import time
        filename = f"cross-plot-{int(time.time() * 1000)}.png"
        output_path = os.path.join(output_dir, filename)
        
        PlotGenerator.generate_cross_plot(
            well_data=well.to_dict(),
            dataset_name=dataset_name,
            x_log=x_log,
            y_log=y_log,
            output_path=output_path
        )
        
        return jsonify({
            "success": True,
            "plotUrl": f"/well-plots/{filename}",
            "message": "Cross plot generated successfully"
        })
    
    except Exception as e:
        import traceback
        print(f"Error generating cross plot: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@visualization_bp.route('/log-data', methods=['GET'])
def get_log_data():
    """Get formatted log data for frontend visualization"""
    try:
        well_name = request.args.get('wellName')
        dataset_name = request.args.get('datasetName')
        project_path = request.args.get('projectPath', os.path.join(os.getcwd(), 'petrophysics-workplace'))
        
        if not well_name or not dataset_name:
            return jsonify({"error": "wellName and datasetName are required"}), 400
        
        # Load well data
        well_manager = WellManager(project_path)
        well = well_manager.get_well_by_name(well_name)
        
        if not well:
            return jsonify({"error": "Well not found"}), 404
        
        # Find dataset
        dataset = None
        for ds in well.datasets:
            if ds.get('name') == dataset_name:
                dataset = ds
                break
        
        if not dataset:
            return jsonify({"error": "Dataset not found"}), 404
        
        return jsonify({
            "success": True,
            "data": {
                "indexLog": dataset.get('index_log', []),
                "indexName": dataset.get('index_name', 'DEPT'),
                "wellLogs": dataset.get('well_logs', []),
                "metadata": dataset.get('metadata', {})
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
