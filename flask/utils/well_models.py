import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

class WellLog:
    """Represents a single well log curve"""
    def __init__(self, mnemonic: str, unit: str = "", description: str = "", data: List[float] = None):
        self.mnemonic = mnemonic
        self.unit = unit
        self.description = description
        self.data = data or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mnemonic": self.mnemonic,
            "unit": self.unit,
            "description": self.description,
            "data": self.data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WellLog':
        return cls(
            mnemonic=data.get("mnemonic", ""),
            unit=data.get("unit", ""),
            description=data.get("description", ""),
            data=data.get("data", [])
        )


class Constant:
    """Represents a well constant/parameter"""
    def __init__(self, mnemonic: str, value: Any, unit: str = "", description: str = ""):
        self.mnemonic = mnemonic
        self.value = value
        self.unit = unit
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mnemonic": self.mnemonic,
            "value": self.value,
            "unit": self.unit,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Constant':
        return cls(
            mnemonic=data.get("mnemonic", ""),
            value=data.get("value"),
            unit=data.get("unit", ""),
            description=data.get("description", "")
        )


class Dataset:
    """Represents a dataset containing well logs"""
    def __init__(self, name: str, logs: List[WellLog] = None, index_log: str = "DEPT"):
        self.name = name
        self.logs = logs or []
        self.index_log = index_log
    
    def add_log(self, log: WellLog):
        self.logs.append(log)
    
    def get_log(self, mnemonic: str) -> Optional[WellLog]:
        for log in self.logs:
            if log.mnemonic == mnemonic:
                return log
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "index_log": self.index_log,
            "logs": [log.to_dict() for log in self.logs]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Dataset':
        dataset = cls(
            name=data.get("name", ""),
            index_log=data.get("index_log", "DEPT")
        )
        for log_data in data.get("logs", []):
            dataset.add_log(WellLog.from_dict(log_data))
        return dataset


class Well:
    """Represents a well with all its data"""
    def __init__(self, name: str, uwi: str = ""):
        self.name = name
        self.uwi = uwi
        self.constants = []
        self.datasets = []
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def add_constant(self, constant: Constant):
        self.constants.append(constant)
    
    def add_dataset(self, dataset: Dataset):
        self.datasets.append(dataset)
    
    def get_dataset(self, name: str) -> Optional[Dataset]:
        for dataset in self.datasets:
            if dataset.name == name:
                return dataset
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize well to dictionary"""
        return {
            "name": self.name,
            "uwi": self.uwi,
            "constants": [c.to_dict() for c in self.constants],
            "datasets": [d.to_dict() for d in self.datasets],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Well':
        """Deserialize well from dictionary"""
        well = cls(
            name=data.get("name", ""),
            uwi=data.get("uwi", "")
        )
        
        for const_data in data.get("constants", []):
            well.add_constant(Constant.from_dict(const_data))
        
        for dataset_data in data.get("datasets", []):
            well.add_dataset(Dataset.from_dict(dataset_data))
        
        well.metadata = data.get("metadata", well.metadata)
        return well
    
    def serialize(self) -> str:
        """Serialize well to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def deserialize(cls, json_str: str) -> 'Well':
        """Deserialize well from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save(self, file_path: str):
        """Save well to .ptrc file"""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(self.serialize())
    
    @classmethod
    def load(cls, file_path: str) -> 'Well':
        """Load well from .ptrc file"""
        with open(file_path, 'r') as f:
            return cls.deserialize(f.read())
