# Dockable Window Manager Application

## Overview

A professional petrophysics data analysis application featuring a dockable window management system inspired by modern IDEs. The application provides an interactive workspace for managing well logs, visualizing data through various plot types, and organizing geological zonation information. Built with React, TypeScript, and Express, it offers a sophisticated drag-and-drop interface for flexible panel arrangement with floating windows, docked layouts, and persistent workspace configurations.

## Recent Changes

### October 13, 2025 - LAS Upload UI & Logging in Python Logs Panel
- **LAS Upload UI in Python Logs Panel**: Direct LAS file upload from bottom panel
  - "Choose LAS File" button to select files
  - "Upload" button to process and import LAS files
  - File name display showing selected file
  - Upload progress indication (button shows "Uploading..." during process)
  - Integrated with project path - automatically uses current project
- **Real-time Upload Logging**: LAS file uploads display detailed logs in Python Logs panel
  - Step-by-step progress messages (no emojis for better compatibility)
  - Color-coded log types: info (blue), success (green), error (red), warning (yellow)
  - Shows: file selection, parsing status, well name, well type, curve count, save paths
  - Error messages displayed clearly with reasons
- **Backend Logging** (flask/routes.py):
  - `/api/wells/create-from-las` endpoint returns structured log array
  - Each log has `message` and `type` (info/success/error/warning)
  - Logs track: file selection, parsing, well details, saving, completion
  - Fixed AttributeError: Uses `ds.well_logs` attribute from fe_data_objects.Dataset
- **Frontend Display** (FeedbackPanelNew.tsx):
  - Upload UI integrated at top of panel
  - Captures logs from API response
  - Displays logs using `window.addPythonLog()` function
  - **Auto-scroll**: Automatically scrolls to show latest messages
  - Smooth scrolling with setTimeout to ensure DOM updates complete
  - Full height log area with native overflow-y-auto
- **User Experience**:
  - Upload LAS files without leaving the Python Logs panel
  - Real-time feedback during upload
  - Clear error messages for debugging
  - Progress tracking from start to completion
  - Auto-scroll keeps latest logs visible

### October 13, 2025 - Replit Environment Setup & Windows Compatibility
- **Development Environment Configuration**:
  - Frontend (Vite + React) runs on port 5000 with 0.0.0.0 host (user-facing)
  - Backend (Flask API) runs on port 5001 with localhost (internal)
  - Vite proxies `/api/*` requests to Flask backend
  - Configured Vite with `allowedHosts: true` for Replit proxy compatibility
- **Production Deployment**:
  - VM deployment configured for always-running server
  - Build step: `npm run build` creates optimized frontend bundle
  - Production: Flask serves both static files and API on port 5000
  - Environment variable `NODE_ENV=production` switches modes
- **Workflow Setup**:
  - Single workflow "Server" runs `bash dev.sh`
  - Starts Flask backend first, then Vite frontend
  - Development mode enables hot reloading for both servers
- **Cross-Platform Path Handling (Windows/Mac/Linux)**:
  - Fixed path validation to support both Windows (C:\) and Unix (/) paths
  - Added path normalization using `os.path.normpath` for compatibility
  - Windows drive letter validation to ensure paths are on same drive
  - Graceful fallback to workspace root for invalid or non-existent paths
  - New `/api/workspace/info` endpoint returns correct workspace path
- **Project Structure**:
  - `dev.sh`: Development startup (Vite on 5000, Flask on 5001)
  - `production.sh`: Production startup (Flask serves all on 5000)
  - `.gitignore`: Updated with Python virtual env and node_modules

### October 13, 2025 - LAS File Processing & Well Management
- **LAS File Upload & Processing**: Complete LAS file import system
  - Upload LAS files directly through the "Create New Well" dialog
  - LAS files are parsed using lasio library and converted to Well objects
  - Wells are saved as `.ptrc` files (JSON format) in the project's `10-WELLS` folder
  - Original LAS files are copied to `02-INPUT_LAS_FOLDER` for reference
  - Real-time LAS file preview showing well info, curves, and data points before upload
  - Removed "Single Well" manual creation tab (users now only upload LAS or CSV files)
- **Well Data Models** (flask/utils/well_models.py):
  - `Well` class: Main well object with metadata, constants, and datasets
  - `Dataset` class: Container for well log curves with index log (default: DEPT)
  - `WellLog` class: Individual log curve with mnemonic, unit, description, and data
  - `Constant` class: Well parameters (UWI, company, location, etc.)
  - Serialize/deserialize methods for JSON persistence (.ptrc format)
- **LAS Processor** (flask/utils/las_processor.py):
  - `parse_las_file()`: Extract well information from LAS files
  - `las_to_well()`: Convert LAS data to Well object with all curves and metadata
  - `save_well_to_project()`: Save well as .ptrc and copy LAS to project folders
  - `preview_las()`: Generate preview information without saving
- **Flask as Main Server**: Replaced Express with Flask as the primary server
  - Flask server runs on port 5000 (main server)
  - Vite dev server runs on port 5173 (proxied through Flask in development)
  - Flask proxies all requests to Vite in development mode
  - Production serves static files from dist folder
- **Project Creation Feature**: Implemented Flask-based project creation
  - Users can create new projects via Project menu > New
  - Projects are created with standard petrophysics folder structure:
    - 01-OUTPUT, 02-INPUT_LAS_FOLDER, 03-DEVIATION, 04-WELL_HEADER
    - 05-TOPS_FOLDER, 06-ZONES_FOLDER, 07-DATA_EXPORTS, 08-VOL_MODELS
    - 09-SPECS, 10-WELLS
  - Validation prevents duplicate projects and invalid names
  - Flask utilities organized in flask/utils/ directory
- **Flask API Routes** (flask/routes.py):
  - `/api/projects/create` - Create new project with standard folder structure
  - `/api/directories/*` - Directory management (list, create, delete, rename)
  - `/api/data/*` - Data explorer (list, file reading)
  - `/api/wells/preview-las` - Preview LAS file content before upload
  - `/api/wells/create-from-las` - Upload and process LAS file, create well as .ptrc
  - `/api/wells/list` - List all wells in a project (reads .ptrc files from 10-WELLS)
- **Development Setup**:
  - dev.sh script starts both Vite and Flask servers
  - npm run dev uses bash script to orchestrate both servers
  - Vite serves on port 5173, Flask proxies on port 5000
- **Deployment Configuration**: 
  - VM deployment with Vite build and Flask production server
  - Flask serves static files from dist folder in production
- **File Preview Feature**: Enhanced Data Explorer with file preview functionality
  - Users can now single-click on files to view their contents in a preview dialog
  - Supports JSON formatting and text file display
  - Includes loading states and error handling
  - Visual indicators show which folders contain files
- **Well File Format (.ptrc)**:
  - Custom JSON-based format for storing well data
  - Extension: `.ptrc` (Petrophysics Resource Container)
  - Structure includes well name, UWI, constants, datasets with logs, and metadata
  - Fully serializable and deserializable using Well class methods
  - Each well is saved as `[well-name].ptrc` in the 10-WELLS folder
- **Feedback Panel Enhancement**: Converted to Python execution log viewer
  - Removed file upload UI from Feedback panel
  - Added terminal-style Python log console with color-coded output (info/error/success/warning)
  - Auto-scroll to latest logs with clear functionality
  - Global window.addPythonLog function for logging from API calls
- **Deployment Configuration**: Set up VM deployment with production build pipeline
  - Build process: Vite frontend build + esbuild backend bundle
  - Production server serves both frontend and API from single process
  - Configured for always-running VM to maintain session state

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Component-Based Design Pattern**
- React with TypeScript for type-safe component development
- Vite as the build tool and development server
- Component structure follows a modular pattern with reusable UI primitives from shadcn/ui

**Window Management System**
- Built with @dnd-kit for drag-and-drop functionality
- Panel states include: visible/hidden, floating/docked, minimized/maximized
- Drop zones for docking panels: left, right, bottom, center
- Persistent geometry tracking (position and size) for floating windows
- Bottom taskbar for minimized panel quick access

**State Management Approach**
- Local component state using React hooks (useState, useEffect)
- Panel configurations stored in component state as Record<string, PanelState>
- No global state management library; state lifted to workspace component level

**Visualization Components**
- Recharts library for cross-plots, log plots, and well log visualization
- Node.js-based data processing for visualization endpoints
- Dynamic data binding from well data to chart components
- Server-side correlation calculations and statistical analysis

**UI Design System**
- Tailwind CSS with custom design tokens
- Dark mode support with CSS variables
- Theme: "new-york" style from shadcn/ui
- Custom color palette: deep slate backgrounds, teal/cyan accents
- Typography: Inter font family with JetBrains Mono for data displays

### Backend Architecture

**Server Framework**
- **Express.js** (Port 5000) - Frontend serving and API gateway
  - TypeScript with ESM module system (type: "module")
  - Development: tsx for hot reloading
  - Production: esbuild for bundling
  - Proxies specific routes to Flask backend
- **Flask** (Port 5001) - Python backend for LAS processing and visualization
  - Flask-CORS enabled for cross-origin requests
  - Modular structure with blueprints
  - Runs as subprocess managed by Express

**API Structure**
- RESTful endpoints under `/api` namespace
- File upload handling with multer (Express) and werkzeug (Flask)
- LAS (Log ASCII Standard) file parsing using lasio
- Project management: CRUD operations for projects and wells
- Visualization generation using matplotlib

**Flask Application Structure**
```
server/flask_app/
├── app.py                    # Main Flask application with blueprints
├── models.py                 # Data models (Well, Dataset, WellLog, Constant)
├── routes/
│   ├── projects.py          # Project management endpoints
│   ├── wells.py             # Well and LAS upload endpoints
│   └── visualization.py     # Plot generation endpoints
└── utils/
    ├── las_processor.py     # WellManager for LAS file processing
    └── plot_generator.py    # PlotGenerator for matplotlib visualizations
```

**File Processing Pipeline**
1. File upload via multipart/form-data to Flask
2. LAS file parsing using lasio library
3. Well and Dataset object creation
4. JSON storage in project's 10-WELLS folder
5. On-demand plot generation using matplotlib

**Session & Storage**
- File-based storage for well data (JSON format)
- In-memory storage for session data (MemStorage class)
- Static file serving from public directory for generated plots
- Petrophysics workspace structure maintained in filesystem

### Data Storage Solutions

**Current Implementation**
- In-memory storage using Map-based data structures
- No persistent database in current state
- User data stored temporarily in MemStorage

**Database Schema (Prepared for PostgreSQL)**
- Drizzle ORM configured with PostgreSQL dialect
- Schema defines users table with UUID primary keys
- Zod validation schemas for type-safe inserts
- Migration setup via drizzle-kit

**File Storage**
- Project files stored in filesystem
- Directory picker for browsing server filesystem
- Well log files (.las, .csv) uploaded and parsed server-side
- Generated plots saved as static images in public directory

### Authentication and Authorization

**Planned Authentication**
- User schema prepared with username/password fields
- Session storage configured with connect-pg-simple
- No active authentication implementation in current codebase
- Routes currently open without auth middleware

### External Dependencies

**Third-Party UI Libraries**
- Radix UI primitives: 20+ components for accessible UI patterns
- @dnd-kit: Drag-and-drop functionality for panel management
- react-rnd: Resizable and draggable components for floating windows
- Recharts: Chart library for data visualization
- cmdk: Command menu implementation

**Data Processing**
- csv-parse: CSV file parsing
- Custom LAS file parser (implemented server-side)

**Python Integration**
- Matplotlib for well log plot generation
- NumPy and Pandas for data processing
- Executed via child process from Node.js server

**Development Tools**
- Vite plugins: runtime error overlay, cartographer (Replit-specific)
- TypeScript with strict mode enabled
- PostCSS with Tailwind CSS and Autoprefixer

**Database & ORM**
- Drizzle ORM with drizzle-kit for migrations
- @neondatabase/serverless for PostgreSQL connection
- Configured but not actively used in current implementation

**Routing & HTTP**
- wouter: Lightweight client-side routing
- @tanstack/react-query: Server state management and caching
- Express middleware for static files and JSON parsing