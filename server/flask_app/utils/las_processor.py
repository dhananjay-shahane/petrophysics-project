import os
import lasio
from datetime import datetime
from typing import Optional
from ..models import Well, Dataset

class WellManager:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.wells_folder = os.path.join(project_path, '10-WELLS')
        os.makedirs(self.wells_folder, exist_ok=True)
    
    def load_wells(self) -> list:
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
        dataset_name = las.params.SET.value if hasattr(las.params, 'SET') and hasattr(las.params.SET, 'value') else "LOG_DATA"
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
            
            reference_dataset = Dataset.reference(0, float(bottom), dataset_name="REFERENCE", dataset_type="REFERENCE", well_name=well_name)
            header_dataset = Dataset.well_header(dataset_name="WELL_HEADER", dataset_type="WELL_HEADER", well_name=well_name)
            
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
