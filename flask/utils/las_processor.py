import os
import lasio
import shutil
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from .fe_data_objects import Well, Dataset, Constant


class LASProcessor:
    """Process LAS files and convert them to Well objects using reference implementation"""
    
    @staticmethod
    def parse_las_file(las_file_path: str) -> Dict[str, Any]:
        """Parse a LAS file and return well information"""
        try:
            las = lasio.read(las_file_path)
            
            well_info = {
                "wellName": las.well.WELL.value if hasattr(las.well, 'WELL') else "UNKNOWN",
                "uwi": las.well.UWI.value if hasattr(las.well, 'UWI') and las.well.UWI else "",
                "company": las.well.COMP.value if hasattr(las.well, 'COMP') and las.well.COMP else "",
                "field": las.well.FLD.value if hasattr(las.well, 'FLD') and las.well.FLD else "",
                "location": las.well.LOC.value if hasattr(las.well, 'LOC') and las.well.LOC else "",
                "province": las.well.PROV.value if hasattr(las.well, 'PROV') and las.well.PROV else "",
                "county": las.well.CNTY.value if hasattr(las.well, 'CNTY') and las.well.CNTY else "",
                "state": las.well.STAT.value if hasattr(las.well, 'STAT') and las.well.STAT else "",
                "country": las.well.CTRY.value if hasattr(las.well, 'CTRY') and las.well.CTRY else "",
                "startDepth": float(las.well.STRT.value) if hasattr(las.well, 'STRT') and las.well.STRT else None,
                "stopDepth": float(las.well.STOP.value) if hasattr(las.well, 'STOP') and las.well.STOP else None,
                "step": float(las.well.STEP.value) if hasattr(las.well, 'STEP') and las.well.STEP else None,
                "null": float(las.well.NULL.value) if hasattr(las.well, 'NULL') and las.well.NULL else -999.25,
                "curveNames": [curve.mnemonic for curve in las.curves],
                "dataPoints": len(las.data) if las.data is not None else 0
            }
            
            return well_info
        except Exception as e:
            raise Exception(f"Failed to parse LAS file: {str(e)}")
    
    @staticmethod
    def las_to_well(las_file_path: str, well_name: Optional[str] = None) -> Well:
        """Convert a LAS file to a Well object using reference implementation"""
        try:
            las = lasio.read(las_file_path)
            
            if not well_name:
                well_name = las.well.WELL.value if hasattr(las.well, 'WELL') and las.well.WELL else Path(las_file_path).stem
            
            dataset_name = las.params.SET.value if hasattr(las.params, 'SET') and las.params.SET else "LAS_DATA"
            bottom = float(las.well.STOP.value) if hasattr(las.well, 'STOP') and las.well.STOP else 0.0
            
            dataset = Dataset.from_las(
                las_file_path, 
                dataset_name=dataset_name,
                dataset_type='Cont',
                well_name=well_name
            )
            
            well = Well(
                date_created=datetime.now(),
                well_name=well_name,
                well_type='Dev',
                datasets=[]
            )
            
            ref_dataset = Dataset.reference(
                top=0,
                bottom=bottom,
                dataset_name='REFERENCE',
                dataset_type='REFERENCE',
                well_name=well_name
            )
            
            wh_dataset = Dataset.well_header(
                dataset_name='WELL_HEADER',
                dataset_type='WELL_HEADER',
                well_name=well_name
            )
            
            const = Constant('WELL_NAME', well_name, 'WELL_NAME')
            wh_dataset.constants.append(const)
            
            well.datasets.append(ref_dataset)
            well.datasets.append(wh_dataset)
            well.datasets.append(dataset)
            
            return well
            
        except Exception as e:
            raise Exception(f"Failed to convert LAS to Well: {str(e)}")
    
    @staticmethod
    def save_well_to_project(well: Well, project_path: str, las_source_file: Optional[str] = None) -> Dict[str, str]:
        """
        Save well to project structure
        - Saves well as .ptrc file in 10-WELLS folder
        - Optionally copies LAS file to 02-INPUT_LAS_FOLDER
        """
        try:
            wells_folder = os.path.join(project_path, "10-WELLS")
            Path(wells_folder).mkdir(parents=True, exist_ok=True)
            
            well_file_path = os.path.join(wells_folder, f"{well.well_name}.ptrc")
            well.serialize(well_file_path)
            
            result = {
                "well_path": well_file_path,
                "well_name": well.well_name
            }
            
            if las_source_file and os.path.exists(las_source_file):
                las_folder = os.path.join(project_path, "02-INPUT_LAS_FOLDER")
                Path(las_folder).mkdir(parents=True, exist_ok=True)
                
                las_dest = os.path.join(las_folder, Path(las_source_file).name)
                shutil.copy2(las_source_file, las_dest)
                result["las_path"] = las_dest
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to save well to project: {str(e)}")
    
    @staticmethod
    def preview_las(las_content: str) -> Dict[str, Any]:
        """Preview LAS file content without saving"""
        try:
            import tempfile
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.las', delete=False) as tmp_file:
                tmp_file.write(las_content)
                tmp_path = tmp_file.name
            
            try:
                preview_info = LASProcessor.parse_las_file(tmp_path)
                return preview_info
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except Exception as e:
            raise Exception(f"Failed to preview LAS file: {str(e)}")
