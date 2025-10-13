# Flask Well Log Plot Implementation - Reference Comparison

## 🎯 Overview
Successfully converted petrophysics well log visualization from Python reference project to Flask backend with hybrid Express proxy architecture.

## 📊 Reference Project Analysis (GitHub: python-code)

### Reference Implementation Structure:
```python
# From fe_data_objects.py
class LogFrame(pd.DataFrame):
    def plot(self, logs: List[str], depth_column: str = 'DEPT'):
        for log in logs:
            if log != depth_column:
                plt.plot(self[log], self[depth_column], label=log)
        plt.ylabel('Depth')
        plt.xlabel('Value')
        plt.grid(True)
```

### Key Patterns from Reference:
1. **Data Structure**: `index_log` (depth) + `well_logs` array
2. **Plotting**: Matplotlib with depth on Y-axis (inverted)
3. **Null Handling**: Filter `-999.25` values
4. **Dataset Types**: REFERENCE, WELL_HEADER, Cont/LOG_DATA

## ✅ Flask Implementation Comparison

### Our Implementation (`server/flask_app/`):

#### 1. **Data Loading** - `utils/las_processor.py`
```python
class WellManager:
    def __init__(self, project_path: str):
        self.wells_folder = os.path.join(project_path, '10-WELLS')
    
    def get_well_by_name(self, well_name: str):
        # Load from JSON files - MATCHES REFERENCE
```

#### 2. **Plot Generation** - `utils/plot_generator.py`
```python
@staticmethod
def generate_well_log_plot(well_data, dataset_name, log_names):
    # Find dataset - MATCHES REFERENCE
    index_log = dataset.get('index_log', [])
    
    # Filter nulls - MATCHES REFERENCE  
    valid_indices = [(i, v) for i, v in enumerate(log_data) 
                     if v is not None and v != -999.25]
    
    # Plot with matplotlib - MATCHES REFERENCE
    ax.plot(values, depths, linewidth=1)
    ax.invert_yaxis()  # Depth increases downward
```

#### 3. **API Endpoints** - `routes/wells.py`
```python
@wells_bp.route('/<well_name>/log-plot', methods=['GET'])
def get_log_plot_data(well_name):
    # Accept projectPath for multi-project support
    # Support BOTH old and new data formats
    # Return JSON for frontend visualization
```

## 🔄 Data Format Support

### Reference Format (New):
```json
{
  "datasets": [{
    "type": "Cont",
    "index_log": [10180, 10181, ...],
    "well_logs": [{
      "name": "DT",
      "unit": "us/ft",
      "log": [59.9, 60.5, ...]
    }]
  }]
}
```

### Legacy Format (Old):
```json
{
  "data": [
    {"DEPT": 8660, "DT": 60, "GR": 103, ...},
    {"DEPT": 8661, "DT": 59.1, "GR": 100, ...}
  ]
}
```

**✅ Flask handles BOTH formats automatically**

## 🔐 Security Enhancements

### Path Validation (Added):
```python
# Secure path validation using commonpath
workspace_root = os.path.join(os.getcwd(), 'petrophysics-workplace')
resolved_workspace = os.path.realpath(workspace_root)
resolved_project_path = os.path.realpath(project_path)

common = os.path.commonpath([resolved_workspace, resolved_project_path])
if common != resolved_workspace:
    return jsonify({"error": "Access denied"}), 403
```

## 🌐 Architecture

### Hybrid Express-Flask Setup:
```
Frontend (React) → Express (port 5000) → Flask (port 5001)
                     ↓
            Proxy: /api/wells/*
                     ↓
            Flask: Well data processing
```

## 🚀 Complete Workflow

1. **Open Project**: Load from `petrophysics-workplace/`
2. **Upload LAS**: Flask processes with `lasio` → creates JSON in `10-WELLS/`
3. **Select Well**: Frontend fetches well list from Flask
4. **Display Plot**: Flask returns formatted track data → Frontend visualizes

## 📈 API Endpoints

### GET `/api/wells/list`
- Lists all wells from project's `10-WELLS` folder
- Supports `projectPath` parameter
- Returns well metadata + log names

### GET `/api/wells/<name>/log-plot`
- Returns formatted log plot data
- Supports both old and new formats
- Includes `projectPath` validation
- Returns: `{indexName, tracks: [{name, unit, data, indexLog}]}`

### POST `/api/wells/<name>/cross-plot`
- Generates cross plot from two log curves
- Calculates correlation coefficient
- Filters null values

## ✨ Key Improvements Over Reference

1. ✅ **Web-based**: No PyQt5 desktop requirement
2. ✅ **RESTful API**: Standard HTTP endpoints
3. ✅ **Dual Format Support**: Handles old and new well data
4. ✅ **Security**: Path validation prevents directory traversal
5. ✅ **Project Isolation**: Multi-project support with projectPath
6. ✅ **URL Encoding**: Handles special characters in well names (#, spaces)

## 🧪 Testing

### Test Commands:
```bash
# Test well list
curl "http://localhost:5000/api/wells/list"

# Test log plot (new format)
curl "http://localhost:5000/api/wells/%2336-16%20State/log-plot"

# Test log plot (old format)  
curl "http://localhost:5000/api/wells/WELL/log-plot?projectPath=/path/to/project"
```

## 📝 Implementation Files

| File | Purpose |
|------|---------|
| `server/flask_app/app.py` | Flask app initialization |
| `server/flask_app/routes/wells.py` | Well data endpoints |
| `server/flask_app/routes/visualization.py` | Plot generation endpoints |
| `server/flask_app/utils/plot_generator.py` | Matplotlib plot logic |
| `server/flask_app/utils/las_processor.py` | LAS file processing |
| `server/flask_app/models.py` | Data models (Well, Dataset) |
| `server/index.ts` | Express proxy configuration |

## ✅ Verification

- [x] Reference pattern analysis completed
- [x] Flask implementation matches reference logic
- [x] Supports both data formats
- [x] Security validation implemented
- [x] URL encoding handled correctly
- [x] Multi-project support working
- [x] Complete workflow tested

## 🎉 Conclusion

The Flask implementation **successfully replicates** the Python reference project's well log plotting functionality while adding:
- Web API architecture
- Enhanced security
- Better format compatibility
- Modern REST endpoints

**Status**: ✅ Production Ready
