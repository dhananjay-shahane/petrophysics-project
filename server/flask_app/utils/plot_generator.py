import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
from typing import List, Dict, Any, Optional
import os

class PlotGenerator:
    @staticmethod
    def _convert_legacy_format(well_data: Dict[str, Any], dataset_name: str) -> Dict[str, Any]:
        """Convert legacy flat data format to new datasets format"""
        if 'data' in well_data and isinstance(well_data['data'], list) and len(well_data['data']) > 0:
            # Legacy format detected
            data_array = well_data['data']
            first_row = data_array[0]
            
            # Extract all column names (log names)
            log_names = list(first_row.keys())
            
            # Assume DEPT or first column is the index
            index_name = 'DEPT' if 'DEPT' in log_names else log_names[0]
            
            # Build index_log
            index_log = [row.get(index_name) for row in data_array]
            
            # Build well_logs
            well_logs = []
            for log_name in log_names:
                if log_name != index_name:
                    log_data = [row.get(log_name) for row in data_array]
                    well_logs.append({
                        'name': log_name,
                        'log': log_data,
                        'unit': ''
                    })
            
            # Create a dataset structure
            return {
                'name': dataset_name,
                'type': 'Cont',
                'index_log': index_log,
                'index_name': index_name,
                'well_logs': well_logs
            }
        return None
    
    @staticmethod
    def generate_well_log_plot(well_data: Dict[str, Any], dataset_name: str, log_names: List[str], output_path: Optional[str] = None) -> str:
        """Generate a well log plot and return the path or base64 encoded image"""
        
        # Find the dataset
        dataset = None
        for ds in well_data.get('datasets', []):
            if ds.get('name') == dataset_name:
                dataset = ds
                break
        
        # If no dataset found, try legacy format conversion
        if not dataset:
            dataset = PlotGenerator._convert_legacy_format(well_data, dataset_name)
        
        if not dataset:
            raise ValueError(f"Dataset {dataset_name} not found")
        
        # Get index log (depth)
        index_log = dataset.get('index_log', [])
        index_name = dataset.get('index_name', 'DEPT')
        
        # Create figure with subplots for each log
        num_logs = len(log_names)
        fig, axes = plt.subplots(1, num_logs, figsize=(4 * num_logs, 12), sharey=True)
        
        if num_logs == 1:
            axes = [axes]
        
        # Plot each log
        for idx, log_name in enumerate(log_names):
            ax = axes[idx]
            
            # Find the log data
            log_data = None
            for well_log in dataset.get('well_logs', []):
                if well_log.get('name') == log_name:
                    log_data = well_log.get('log', [])
                    unit = well_log.get('unit', '')
                    break
            
            if log_data:
                # Filter out null values
                valid_indices = [(i, v) for i, v in enumerate(log_data) if v is not None and v != -999.25]
                if valid_indices:
                    indices, values = zip(*valid_indices)
                    depths = [index_log[i] for i in indices]
                    
                    ax.plot(values, depths, linewidth=1)
                    ax.set_xlabel(f"{log_name} ({unit})")
                    ax.grid(True, alpha=0.3)
                    ax.invert_yaxis()
                    
                    if idx == 0:
                        ax.set_ylabel(f"{index_name} (m)")
        
        plt.suptitle(f"Well Log Plot - {well_data.get('well_name', 'Unknown')}", fontsize=14)
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        else:
            # Return base64 encoded image
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            return f"data:image/png;base64,{image_base64}"
    
    @staticmethod
    def generate_cross_plot(well_data: Dict[str, Any], dataset_name: str, x_log: str, y_log: str, output_path: Optional[str] = None) -> str:
        """Generate a cross plot and return the path or base64 encoded image"""
        
        # Find the dataset
        dataset = None
        for ds in well_data.get('datasets', []):
            if ds.get('name') == dataset_name:
                dataset = ds
                break
        
        # If no dataset found, try legacy format conversion
        if not dataset:
            dataset = PlotGenerator._convert_legacy_format(well_data, dataset_name)
        
        if not dataset:
            raise ValueError(f"Dataset {dataset_name} not found")
        
        # Get log data
        x_data = None
        y_data = None
        x_unit = ''
        y_unit = ''
        
        for well_log in dataset.get('well_logs', []):
            if well_log.get('name') == x_log:
                x_data = well_log.get('log', [])
                x_unit = well_log.get('unit', '')
            if well_log.get('name') == y_log:
                y_data = well_log.get('log', [])
                y_unit = well_log.get('unit', '')
        
        if x_data is None or y_data is None:
            raise ValueError("Log data not found")
        
        # Filter out null values
        valid_pairs = [(x, y) for x, y in zip(x_data, y_data) if x is not None and y is not None and x != -999.25 and y != -999.25]
        
        if not valid_pairs:
            raise ValueError("No valid data points for cross plot")
        
        x_values, y_values = zip(*valid_pairs)
        
        # Create cross plot
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.scatter(x_values, y_values, alpha=0.5, s=10)
        ax.set_xlabel(f"{x_log} ({x_unit})")
        ax.set_ylabel(f"{y_log} ({y_unit})")
        ax.set_title(f"Cross Plot: {y_log} vs {x_log} - {well_data.get('well_name', 'Unknown')}")
        ax.grid(True, alpha=0.3)
        
        # Calculate and display correlation
        correlation = np.corrcoef(x_values, y_values)[0, 1]
        ax.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        else:
            # Return base64 encoded image
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            return f"data:image/png;base64,{image_base64}"
