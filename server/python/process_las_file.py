#!/usr/bin/env python
import sys
import json
import os
from datetime import datetime
import lasio

def process_las_file(las_file_path, project_path):
    try:
        wells_folder = os.path.join(project_path, '10-WELLS')
        os.makedirs(wells_folder, exist_ok=True)
        
        las = lasio.read(las_file_path)
        
        well_name = las.well.WELL.value if hasattr(las.well, 'WELL') else "Unknown"
        dataset_name = las.params.SET.value if hasattr(las.params, 'SET') and hasattr(las.params.SET, 'value') else "LOG_DATA"
        top = las.well.STRT.value if hasattr(las.well, 'STRT') else 0
        bottom = las.well.STOP.value if hasattr(las.well, 'STOP') else 0
        
        well_json_path = os.path.join(wells_folder, f"{well_name}.json")
        
        index_name = getattr(las, 'index_name', 'DEPT')
        index_log = las.index.tolist()
        
        well_logs = []
        for curve in las.curves:
            if curve.mnemonic != index_name:
                well_log = {
                    "name": curve.mnemonic,
                    "date": datetime.now().isoformat(),
                    "description": curve.descr or "",
                    "log": curve.data.tolist(),
                    "log_type": "continuous",
                    "interpolation": "linear",
                    "unit": curve.unit or ""
                }
                well_logs.append(well_log)
        
        metadata = {
            "STRT": float(top) if top else 0,
            "STOP": float(bottom) if bottom else 0,
            "STEP": float(las.well.STEP.value) if hasattr(las.well, 'STEP') else 0,
            "NULL": float(las.well.NULL.value) if hasattr(las.well, 'NULL') else -999.25,
        }
        
        dataset = {
            "date_created": datetime.now().isoformat(),
            "name": dataset_name,
            "type": "Cont",
            "wellname": well_name,
            "constants": [],
            "index_log": index_log,
            "index_name": index_name,
            "well_logs": well_logs,
            "metadata": metadata
        }
        
        if os.path.exists(well_json_path):
            with open(well_json_path, 'r') as f:
                existing_well = json.load(f)
            existing_well['datasets'].append(dataset)
            well = existing_well
            message = f"Dataset '{dataset_name}' added to existing well '{well_name}'"
        else:
            well_id = f"well-{int(datetime.now().timestamp() * 1000)}"
            
            reference_dataset = {
                "date_created": datetime.now().isoformat(),
                "name": "REFERENCE",
                "type": "REFERENCE",
                "wellname": well_name,
                "constants": [],
                "index_log": [0, float(bottom)],
                "index_name": "DEPT",
                "well_logs": [],
                "metadata": {"top": 0, "bottom": float(bottom)}
            }
            
            header_dataset = {
                "date_created": datetime.now().isoformat(),
                "name": "WELL_HEADER",
                "type": "WELL_HEADER",
                "wellname": well_name,
                "constants": [{"name": "WELL_NAME", "value": well_name}],
                "index_log": [],
                "index_name": "DEPT",
                "well_logs": [],
                "metadata": {}
            }
            
            well = {
                "id": well_id,
                "date_created": datetime.now().isoformat(),
                "well_name": well_name,
                "well_type": "Dev",
                "datasets": [reference_dataset, header_dataset, dataset]
            }
            message = f"New well '{well_name}' created successfully"
        
        with open(well_json_path, 'w') as f:
            json.dump(well, f, indent=2)
        
        result = {
            "success": True,
            "message": message,
            "well": well
        }
        print(json.dumps(result))
        
    except Exception as e:
        result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(result))
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"success": False, "error": "Missing arguments"}))
        sys.exit(1)
    
    las_file_path = sys.argv[1]
    project_path = sys.argv[2]
    
    process_las_file(las_file_path, project_path)
