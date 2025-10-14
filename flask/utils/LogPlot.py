"""
Well Log Plotting Module (Flask/Web adapted from PyQt LogPlot.py)
Provides functionality for creating well log plots with matplotlib
"""

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for web
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import io
import base64
import numpy as np


class LogPlotManager:
    """
    Manages well log plotting functionality
    Adapted from PyQt LogPlot.py for Flask web backend
    """
    
    def __init__(self):
        self.docks = []
        self.shared_axis = None
        self.main_figure = None
    
    def create_log_plot(self, well_data, log_names, index_name='DEPTH'):
        """
        Create a well log plot with multiple tracks
        Based on GitHub repo logplotclass.py matplotlib implementation
        
        Args:
            well_data: Well object with datasets
            log_names: List of log names to plot
            index_name: Name of the index (typically 'DEPTH')
            
        Returns:
            Base64 encoded PNG image
        """
        print(f"[LogPlot] Creating log plot for {len(log_names)} logs: {log_names}")
        
        if not log_names:
            print("[LogPlot] No log names provided")
            return None
        
        # Number of tracks (one per log)
        num_tracks = len(log_names)
        
        # Create figure with horizontal layout (tracks side by side)
        # Similar to GitHub repo's MainFigureWidget and MatplotlibDockWidget
        fig = Figure(figsize=(4 * num_tracks, 12))
        print(f"[LogPlot] Created figure with {num_tracks} tracks")
        
        # Collect log data
        tracks_data = []
        shared_index = None
        
        for log_name in log_names:
            print(f"[LogPlot] Searching for log: {log_name}")
            # Search through all datasets
            for dataset in well_data.datasets:
                # Look for the log in dataset's well_logs
                for well_log in dataset.well_logs:
                    if well_log.name == log_name:
                        tracks_data.append({
                            'name': log_name,
                            'log': well_log.log,
                            'index': dataset.index_log,
                            'index_name': dataset.index_name or index_name
                        })
                        if shared_index is None and dataset.index_log:
                            shared_index = dataset.index_log
                        print(f"[LogPlot] Found {log_name} with {len(well_log.log)} points")
                        break
                if tracks_data and tracks_data[-1]['name'] == log_name:
                    break
        
        if not tracks_data:
            print("[LogPlot] ERROR: No track data found")
            return None
            
        if shared_index is None:
            print("[LogPlot] ERROR: No shared index (DEPTH) found")
            return None
        
        print(f"[LogPlot] Successfully collected {len(tracks_data)} tracks")
        
        # Create subplots with shared y-axis
        axes = []
        for i, track in enumerate(tracks_data):
            if i == 0:
                ax = fig.add_subplot(1, num_tracks, i + 1)
                self.shared_axis = ax
            else:
                ax = fig.add_subplot(1, num_tracks, i + 1, sharey=axes[0])
            
            axes.append(ax)
            
            # Plot the log curve
            log_values = track['log']
            index_values = track['index'] or shared_index
            
            # Filter valid data
            valid_data = [(idx, val) for idx, val in zip(index_values, log_values) 
                         if val is not None and not np.isnan(val)]
            
            if valid_data:
                valid_idx, valid_vals = zip(*valid_data)
                
                # Plot with data on x-axis and depth on y-axis
                ax.plot(valid_vals, valid_idx, linewidth=1, color='blue')
                
                # Configure axes
                ax.set_xlabel(track['name'], fontsize=10, fontweight='bold')
                ax.xaxis.set_label_position('top')
                ax.xaxis.tick_top()
                
                # Invert y-axis (depth increases downward)
                if i == 0:
                    ax.invert_yaxis()
                    ax.set_ylabel(track['index_name'], fontsize=10, fontweight='bold')
                else:
                    ax.tick_params(axis='y', labelleft=False)
                
                # Grid
                ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
                ax.set_axisbelow(True)
        
        # Adjust layout
        fig.tight_layout()
        
        # Convert to base64 PNG
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close(fig)
        
        return img_base64
    
    def add_dock(self, log_name, log_data, shared_axis):
        """
        Add a dock/track for a log
        
        Args:
            log_name: Name of the log
            log_data: Log data array
            shared_axis: Shared axis (depth) for alignment
        """
        dock_data = {
            'name': log_name,
            'data': log_data,
            'shared_axis': shared_axis
        }
        self.docks.append(dock_data)
        return dock_data
    
    def remove_dock(self, dock_index=None):
        """Remove a dock/track"""
        if self.docks:
            if dock_index is not None and 0 <= dock_index < len(self.docks):
                self.docks.pop(dock_index)
            else:
                self.docks.pop()
    
    def clear_docks(self):
        """Clear all docks/tracks"""
        self.docks = []
