#!/usr/bin/env python3
import sys
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

def generate_well_log_plot(json_file_path, output_image_path):
    try:
        with open(json_file_path, 'r') as f:
            well_data = json.load(f)
        
        if not well_data.get('data') or len(well_data['data']) == 0:
            raise ValueError("No well log data available")
        
        df = pd.DataFrame(well_data['data'])
        logs = well_data.get('logs', [])
        
        depth_key = None
        for key in ['DEPT', 'DEPTH', 'Depth', 'depth']:
            if key in df.columns:
                depth_key = key
                break
        
        if not depth_key:
            raise ValueError("No depth column found in data")
        
        curve_columns = [col for col in logs if col != depth_key and col in df.columns]
        
        if len(curve_columns) == 0:
            raise ValueError("No curve data available")
        
        num_tracks = min(len(curve_columns), 6)
        fig, axes = plt.subplots(nrows=1, ncols=num_tracks, figsize=(3*num_tracks, 12), sharey=True)
        
        if num_tracks == 1:
            axes = [axes]
        
        colors = ['#2563eb', '#9333ea', '#059669', '#dc2626', '#f59e0b', '#8b5cf6']
        
        for i, curve_name in enumerate(curve_columns[:num_tracks]):
            ax = axes[i]
            
            curve_data = df[curve_name].dropna()
            depth_data = df.loc[curve_data.index, depth_key]
            
            ax.plot(curve_data, depth_data, color=colors[i % len(colors)], linewidth=1)
            ax.set_xlabel(curve_name, fontsize=10)
            ax.grid(True, alpha=0.3, linewidth=0.5)
            ax.tick_params(axis='both', labelsize=8)
            
            if i == 0:
                ax.set_ylabel('Depth', fontsize=10)
        
        for ax in axes:
            ax.set_ylim(df[depth_key].max(), df[depth_key].min())
            ax.spines['top'].set_visible(True)
        
        well_name = well_data.get('metadata', {}).get('well', {}).get('WELL', {}).get('value', 'Unknown Well')
        fig.suptitle(f'Well Log Plot: {well_name}', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_image_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return {
            "success": True,
            "message": f"Well log plot generated successfully",
            "output_path": output_image_path,
            "tracks": num_tracks,
            "curves": curve_columns[:num_tracks]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(json.dumps({
            "success": False,
            "error": "Usage: python generate_well_log_plot.py <json_file_path> <output_image_path>"
        }))
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    output_image_path = sys.argv[2]
    
    result = generate_well_log_plot(json_file_path, output_image_path)
    print(json.dumps(result))
