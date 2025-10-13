from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Union
from datetime import datetime
import json
import lasio

@dataclass
class Constant:
    name: str
    value: Any
    tag: str = ""
    
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
        
        index_name = getattr(las, 'index_name', 'DEPT')
        for curve in las.curves:
            if curve.mnemonic != index_name:
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
            index_name=index_name,
            well_logs=well_logs,
            metadata=metadata
        )
    
    @staticmethod
    def reference(top: float, bottom: float, dataset_name: str, dataset_type: str, well_name: str) -> 'Dataset':
        return Dataset(
            date_created=datetime.now().isoformat(),
            name=dataset_name,
            type=dataset_type,
            wellname=well_name,
            index_log=[top, bottom],
            metadata={"top": top, "bottom": bottom}
        )
    
    @staticmethod
    def well_header(dataset_name: str, dataset_type: str, well_name: str) -> 'Dataset':
        return Dataset(
            date_created=datetime.now().isoformat(),
            name=dataset_name,
            type=dataset_type,
            wellname=well_name,
            constants=[{"name": "WELL_NAME", "value": well_name}]
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
        import os
        filename = os.path.join(folder_path, f"{self.well_name}.json")
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        return filename
    
    @staticmethod
    def deserialize(file_path: str) -> 'Well':
        with open(file_path, 'r') as f:
            data = json.load(f)
        return Well(**data)
