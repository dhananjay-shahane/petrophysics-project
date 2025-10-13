#!/usr/bin/env python3
"""Test script to verify Flask visualization endpoints"""

import requests
import json
import os

BASE_URL = "http://localhost:5001"

def test_las_upload():
    """Test LAS file upload"""
    print("=" * 50)
    print("Testing LAS File Upload")
    print("=" * 50)
    
    # Upload a LAS file
    las_file_path = "test-data/49-005-30258.las"
    
    if not os.path.exists(las_file_path):
        print(f"Error: LAS file not found at {las_file_path}")
        return None
    
    with open(las_file_path, 'rb') as f:
        files = {'file': ('test.las', f, 'application/octet-stream')}
        data = {'wellType': 'Dev'}
        
        response = requests.post(f"{BASE_URL}/api/wells/upload-las", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Upload successful!")
            print(f"  Well Name: {result.get('well_name')}")
            print(f"  Message: {result.get('message')}")
            return result.get('well_name')
        else:
            print(f"✗ Upload failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return None

def test_get_wells():
    """Test getting all wells"""
    print("\n" + "=" * 50)
    print("Testing Get All Wells")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/api/wells/")
    
    if response.status_code == 200:
        wells = response.json()
        print(f"✓ Found {len(wells)} well(s)")
        for well in wells:
            print(f"  - {well.get('well_name')}")
        return wells
    else:
        print(f"✗ Failed to get wells: {response.status_code}")
        return []

def test_log_plot(well_name):
    """Test log plot endpoint"""
    print("\n" + "=" * 50)
    print(f"Testing Log Plot for {well_name}")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/api/wells/{well_name}/log-plot")
    
    if response.status_code == 200:
        plot_data = response.json()
        print(f"✓ Log plot data retrieved successfully!")
        print(f"  Well Name: {plot_data.get('wellName')}")
        print(f"  Number of tracks: {len(plot_data.get('tracks', []))}")
        
        for i, track in enumerate(plot_data.get('tracks', [])[:3]):
            print(f"  Track {i+1}: {track.get('name')} ({track.get('unit')})")
            print(f"    Data points: {len(track.get('data', []))}")
        
        return plot_data
    else:
        print(f"✗ Failed to get log plot: {response.status_code}")
        print(f"  Error: {response.text}")
        return None

def test_cross_plot(well_name):
    """Test cross plot endpoint"""
    print("\n" + "=" * 50)
    print(f"Testing Cross Plot for {well_name}")
    print("=" * 50)
    
    # Get available curves first
    response = requests.get(f"{BASE_URL}/api/wells/{well_name}/log-plot")
    if response.status_code == 200:
        plot_data = response.json()
        tracks = plot_data.get('tracks', [])
        
        if len(tracks) >= 2:
            x_curve = tracks[0].get('name')
            y_curve = tracks[1].get('name')
            
            cross_plot_data = {
                'xCurve': x_curve,
                'yCurve': y_curve
            }
            
            response = requests.post(
                f"{BASE_URL}/api/wells/{well_name}/cross-plot",
                json=cross_plot_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Cross plot data generated successfully!")
                print(f"  X Curve: {result.get('xCurve')}")
                print(f"  Y Curve: {result.get('yCurve')}")
                print(f"  Data points: {len(result.get('data', []))}")
                print(f"  Correlation: {result.get('correlation', 0):.4f}")
                return result
            else:
                print(f"✗ Failed to generate cross plot: {response.status_code}")
                print(f"  Error: {response.text}")
        else:
            print("  Not enough tracks for cross plot")
    
    return None

if __name__ == "__main__":
    print("Flask Visualization Test Suite")
    print("=" * 50)
    
    # Test upload
    well_name = test_las_upload()
    
    if well_name:
        # Test get wells
        wells = test_get_wells()
        
        # Test log plot
        log_plot_data = test_log_plot(well_name)
        
        # Test cross plot
        cross_plot_data = test_cross_plot(well_name)
        
        print("\n" + "=" * 50)
        print("Test Summary")
        print("=" * 50)
        print(f"✓ LAS Upload: {'Success' if well_name else 'Failed'}")
        print(f"✓ Get Wells: {'Success' if wells else 'Failed'}")
        print(f"✓ Log Plot: {'Success' if log_plot_data else 'Failed'}")
        print(f"✓ Cross Plot: {'Success' if cross_plot_data else 'Failed'}")
    else:
        print("\n✗ Upload failed, skipping other tests")
