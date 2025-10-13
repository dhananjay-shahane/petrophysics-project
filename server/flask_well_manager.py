from flask import Flask, request, jsonify
from flask_cors import CORS
import lasio
import json
import os
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class Constant:
    name: str
    value: Any
    
@dataclass
class WellLog:
    name: str
    date: str
    description: str
    log: List[float]
    log_type: str
    interpolation: str
    unit: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "date": self.date,
            "description": self.description,
            "log": self.log,
            "log_type": self.log_type,
            "interpolation": self.interpolation,
            "unit": self.unit
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'WellLog':
        return WellLog(**data)

@dataclass
class Dataset:
    date_created: str
    name: str
    type: str
    wellname: str
    constants: List[Dict[str, Any]] = field(default_factory=list)
    index_log: List[float] = field(default_factory=list)
    index_name: str = "DEPT"
    well_logs: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "date_created": self.date_created,
            "name": self.name,
            "type": self.type,
            "wellname": self.wellname,
            "constants": self.constants,
            "index_log": self.index_log,
            "index_name": self.index_name,
            "well_logs": self.well_logs,
            "metadata": self.metadata
        }
    
    @staticmethod
    def from_las(las_file_path: str, dataset_name: str, dataset_type: str, well_name: str) -> 'Dataset':
        las = lasio.read(las_file_path)
        
        index_log = las.index.tolist()
        well_logs = []
        
        for curve in las.curves:
            if curve.mnemonic != las.index_name:
                well_log = WellLog(
                    name=curve.mnemonic,
                    date=datetime.now().isoformat(),
                    description=curve.descr or "",
                    log=curve.data.tolist(),
                    log_type="continuous",
                    interpolation="linear",
                    unit=curve.unit or ""
                )
                well_logs.append(well_log.to_dict())
        
        metadata = {
            "STRT": float(las.well.STRT.value) if hasattr(las.well, 'STRT') else 0,
            "STOP": float(las.well.STOP.value) if hasattr(las.well, 'STOP') else 0,
            "STEP": float(las.well.STEP.value) if hasattr(las.well, 'STEP') else 0,
            "NULL": float(las.well.NULL.value) if hasattr(las.well, 'NULL') else -999.25,
        }
        
        return Dataset(
            date_created=datetime.now().isoformat(),
            name=dataset_name,
            type=dataset_type,
            wellname=well_name,
            index_log=index_log,
            index_name=las.index_name,
            well_logs=well_logs,
            metadata=metadata
        )

@dataclass
class Well:
    date_created: str
    well_name: str
    well_type: str
    id: str
    datasets: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "date_created": self.date_created,
            "well_name": self.well_name,
            "well_type": self.well_type,
            "datasets": self.datasets
        }
    
    def serialize(self, folder_path: str):
        filename = os.path.join(folder_path, f"{self.well_name}.json")
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        return filename
    
    @staticmethod
    def deserialize(file_path: str) -> 'Well':
        with open(file_path, 'r') as f:
            data = json.load(f)
        return Well(**data)

class WellManager:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.wells_folder = os.path.join(project_path, '10-WELLS')
        os.makedirs(self.wells_folder, exist_ok=True)
    
    def load_wells(self) -> List[Well]:
        wells = []
        if os.path.exists(self.wells_folder):
            for file in os.listdir(self.wells_folder):
                if file.endswith('.json'):
                    file_path = os.path.join(self.wells_folder, file)
                    try:
                        well = Well.deserialize(file_path)
                        wells.append(well)
                    except Exception as e:
                        print(f"Error loading well from {file}: {e}")
        return wells
    
    def get_well_by_name(self, well_name: str) -> Optional[Well]:
        file_path = os.path.join(self.wells_folder, f"{well_name}.json")
        if os.path.exists(file_path):
            return Well.deserialize(file_path)
        return None
    
    def create_well_from_las(self, las_file_path: str, well_type: str = "Dev") -> Well:
        las = lasio.read(las_file_path)
        
        well_name = las.well.WELL.value if hasattr(las.well, 'WELL') else "Unknown"
        dataset_name = las.params.SET.value if hasattr(las.params, 'SET') else "LOG_DATA"
        top = las.well.STRT.value if hasattr(las.well, 'STRT') else 0
        bottom = las.well.STOP.value if hasattr(las.well, 'STOP') else 0
        
        existing_well = self.get_well_by_name(well_name)
        
        dataset = Dataset.from_las(
            las_file_path,
            dataset_name=dataset_name,
            dataset_type='Cont',
            well_name=well_name
        )
        
        if existing_well:
            existing_well.datasets.append(dataset.to_dict())
            existing_well.serialize(self.wells_folder)
            return existing_well
        else:
            well_id = f"well-{int(datetime.now().timestamp() * 1000)}"
            
            reference_dataset = Dataset(
                date_created=datetime.now().isoformat(),
                name="REFERENCE",
                type="REFERENCE",
                wellname=well_name,
                index_log=[0, float(bottom)],
                metadata={"top": 0, "bottom": float(bottom)}
            )
            
            header_dataset = Dataset(
                date_created=datetime.now().isoformat(),
                name="WELL_HEADER",
                type="WELL_HEADER",
                wellname=well_name,
                constants=[{"name": "WELL_NAME", "value": well_name}]
            )
            
            new_well = Well(
                id=well_id,
                date_created=datetime.now().isoformat(),
                well_name=well_name,
                well_type=well_type,
                datasets=[
                    reference_dataset.to_dict(),
                    header_dataset.to_dict(),
                    dataset.to_dict()
                ]
            )
            
            new_well.serialize(self.wells_folder)
            return new_well

app = Flask(__name__)
CORS(app)

PROJECT_PATH = os.path.join(os.getcwd(), 'petrophysics-workplace')
well_manager = WellManager(PROJECT_PATH)

@app.route('/api/wells', methods=['GET'])
def get_wells():
    wells = well_manager.load_wells()
    return jsonify([well.to_dict() for well in wells])

@app.route('/api/wells/<well_name>', methods=['GET'])
def get_well(well_name):
    well = well_manager.get_well_by_name(well_name)
    if well:
        return jsonify(well.to_dict())
    return jsonify({"error": "Well not found"}), 404

@app.route('/api/wells/upload-las', methods=['POST'])
def upload_las():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not file.filename.endswith('.las'):
        return jsonify({"error": "File must be a .las file"}), 400
    
    temp_folder = os.path.join(PROJECT_PATH, '02-INPUT_LAS_FOLDER')
    os.makedirs(temp_folder, exist_ok=True)
    
    las_path = os.path.join(temp_folder, file.filename)
    file.save(las_path)
    
    try:
        well = well_manager.create_well_from_las(las_path, well_type='Dev')
        return jsonify({
            "success": True,
            "message": f"Well '{well.well_name}' created/updated successfully",
            "well": well.to_dict()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
