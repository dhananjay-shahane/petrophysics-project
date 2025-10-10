# Well Log Visualization Application

## Overview
A professional well log data visualization and management application designed for the oil and gas industry. Built with React, Express, and TypeScript, featuring a modern dockable window manager inspired by IDEs like VS Code and Figma.

## Purpose
This application provides geologists and petrophysicists with tools to:
- Manage well log data projects
- Visualize well logs with multiple tracks (Gamma Ray, Deep Res., PhiT, Sw)
- Import and process CSV/LAS files
- Create and organize project structures
- Manage zonation and tops data

## Project Structure

### Frontend (React + Vite)
- **Location**: `client/src/`
- **Technology**: React 18, TypeScript, Tailwind CSS, Vite
- **Key Features**:
  - Dockable window system with drag-and-drop
  - Well log plotting with canvas rendering
  - Project management UI
  - File browser and data import
  - Dark/Light theme support

### Backend (Express)
- **Location**: `server/`
- **Technology**: Express.js, Node.js 20
- **API Endpoints**:
  - `/api/directories/list` - Browse file system
  - `/api/projects/create` - Create new projects
  - `/api/projects/save` - Save project data
  - `/api/projects/load/:fileName` - Load projects
  - `/api/projects/list` - List all projects

### Storage
- **Type**: File-based JSON storage
- **Location**: `database/` folder (auto-created)
- **Format**: Project data saved as timestamped JSON files

## Current State
- ✅ Development server running on port 5000
- ✅ Vite configured with proxy support (allowedHosts: true)
- ✅ All UI panels functional and dockable
- ✅ Well log visualization rendering
- ✅ Project structure creation working
- ✅ File-based storage operational
- ⚠️ PostgreSQL database schema defined but using in-memory storage

## Architecture
- **Single Server**: Express serves both API and frontend
- **Port**: 5000 (development and production)
- **Dev Mode**: Vite middleware with HMR
- **Prod Mode**: Serves pre-built static files from `dist/public`

## Configuration Files
- `package.json` - Dependencies and scripts
- `vite.config.ts` - Frontend build configuration
- `tsconfig.json` - TypeScript settings
- `tailwind.config.ts` - Styling configuration
- `drizzle.config.ts` - Database migrations (optional)

## Design Guidelines
See `design_guidelines.md` for detailed UI/UX specifications including:
- Color palette (teal/cyan theme)
- Typography system
- Layout primitives
- Component patterns
- Window management behavior

## Recent Changes (October 10, 2025)

### Well Selection & Visualization Integration ✅ (Latest - October 10, 2025)
- ✅ **Connected Wells Panel to Well Log Plot**:
  - Click any well in Wells panel to select it (highlights with border)
  - Selected well data automatically loads from JSON file
  - Well Log Plot displays selected well's curves in real-time
  - Shows curve names from actual well data (DEPT, DT, RESD, SP, GR, etc.)
  - Real well log visualization with proper depth scaling
  - Displays "No well selected" message when no well is chosen
  - Displays "Loading well..." message while data loads
- ✅ **Real Data Visualization**:
  - Plots actual LAS curve data (not mock/sample data)
  - Auto-scales each curve to fit track width
  - Normalizes depth range to canvas height
  - Color-coded curves for easy identification
  - Up to 8 tracks displayed simultaneously
  - Excludes DEPT/DEPTH from display curves (used for Y-axis only)
- ✅ **Data Flow**:
  1. User opens project → Wells load automatically
  2. User clicks well in Wells panel → Well selected
  3. System loads well JSON data (if not loaded)
  4. Well Log Plot receives selected well
  5. Canvas renders actual curve data
- ✅ **State Management**:
  - selectedWell state tracks currently selected well
  - Well data cached in wells array after first load
  - Auto-updates visualization when selection changes

### Enhanced LAS File Parsing & Well Creation ✅ (October 10, 2025)
- ✅ **Improved LAS File to Well JSON Conversion**:
  - Enhanced LAS parser to extract all well log data from ASCII section
  - Parser extracts: well info, company, field, location, depth range, curves, and data points
  - Data properly structured: `data` array contains all depth and curve values
  - Each data point includes all curves (DEPT, DT, RESD, SP, GR, etc.)
  - Metadata includes: lasFile, depthMin, depthMax, location, company, field, step, null value
- ✅ **Live LAS File Preview**:
  - Added preview API endpoint: `/api/wells/preview-las`
  - Shows parsed data before upload: well name, company, location, depth range, curves, data points
  - Visual confirmation of successful parsing with green checkmark
  - Preview updates automatically when file is selected
- ✅ **Enhanced Create Well Dialog**:
  - Shows real-time preview of LAS file contents
  - Displays curve names and data point count
  - Better visual feedback for users
  - Maintains existing CSV and single well creation tabs
- ✅ **Data Structure**:
  - Well JSON format: `{ id, name, description, data[], logs[], metadata{} }`
  - `data` array: array of objects, each with curve name -> value mapping
  - `logs` array: list of curve names (e.g., ["DEPT", "GR", "RESD", "SP"])
  - Ready for visualization in Well Log Plot panel

### Fresh GitHub Import - Replit Environment Setup ✅ (October 10, 2025)
- ✅ **Fresh GitHub clone imported and configured successfully**
- ✅ Installed all npm dependencies (520 packages)
- ✅ Resolved all LSP/TypeScript errors - codebase clean
- ✅ Configured "Server" workflow: `npm run dev` on port 5000 with webview output
- ✅ Verified application functionality - all features working correctly
- ✅ Confirmed Vite configuration: host 0.0.0.0, allowedHosts: true (Replit proxy compatible)
- ✅ Confirmed Express server configuration: host 0.0.0.0, port 5000
- ✅ **Configured deployment for production**:
  - Deployment target: autoscale (stateless web app)
  - Build command: `npm run build`
  - Run command: `npm start`
  - Production build tested successfully (dist/public + dist/index.js)
  - Frontend bundle: 886.89 kB, Backend bundle: 32.0 kB
- ✅ All panels functional: Wells, Well Log Plot, Data Browser, Zonation, Feedback
- ✅ Well log visualization rendering correctly with sample data
- ✅ Dockable panel system working (minimize, maximize, close, drag)
- ✅ Theme toggle (dark/light mode) operational
- ✅ Development server running with HMR (Hot Module Replacement)
- ✅ Backend and frontend integrated in single Express server
- ✅ Import complete - ready for development and deployment

### UI/UX Improvements
- ✅ **Updated Directory Picker with Rounded Folder Selection UI**
  - Changed title from "Choose Directory Path" to "Select Folder"
  - Implemented single-click to select folder, double-click to navigate
  - Added rounded/circular folder icons with selection highlighting
  - Folders now show with rounded-2xl borders and scale effect on selection
  - Selected folder displays with primary color highlight and shadow
  - Button text dynamically shows selected folder name
  - Improved visual feedback with smooth transitions
  - **Multi-OS Path Support with Auto-Fallback**:
    - Detects OS and tries appropriate path (Windows: C:\petrophysics-workplace, Linux: /home/runner/workspace/petrophysics-workplace)
    - Automatically tries alternative paths if primary path fails
    - Supports: Linux, Windows, root paths, and relative paths
    - Shows notification when using alternative path

### New Features Added
- ✅ **Well Creation System** (October 10, 2025)
  - **CSV Upload for Multiple Wells**:
    - Upload CSV files to create multiple wells at once
    - Validates well names and depth ranges (depth_max > depth_min)
    - Generates realistic LAS files automatically for each well
    - Row-level error reporting for validation issues
    - Saves well data as JSON in project's 10-WELLS folder
  - **LAS File Upload for Single Well**:
    - Upload LAS files to create individual wells
    - Well name automatically extracted from LAS file
    - Server-side LAS parser extracts metadata (Well, Curve, ASCII sections)
    - Parses company, field, location, depth information
    - Auto-generates unique well names if duplicate exists (e.g., WELL_1, WELL_2)
    - Copies LAS file to project's 02-INPUT_LAS_FOLDER
    - Generates well data with curve information
  - **Auto-Loading Wells on Project Open**:
    - Wells automatically load when project is opened
    - New `/api/wells/list` endpoint with workspace security validation
    - Path normalization prevents directory traversal attacks
    - Displays wells in Wells panel immediately on project selection
    - Returns empty array gracefully when 10-WELLS folder missing

- ✅ **View Menu with Visualization Windows**
  - Added new "View" menu in menu bar
  - Cross Plot window - scatter plot for correlating well log parameters
  - Log Plot window - line chart for displaying well logs vs depth
  - Both windows use DockablePanel wrapper like Well Log Plot
  - Windows can be docked, floated, minimized, and resized
  
- ✅ **Enhanced Feedback Panel**
  - Now shows full file path when CSV/LAS files are dropped
  - Displays file name, size, and path information
  - Better file information visibility

### Previous Features (from original setup)
- Made DATABASE_URL optional (file storage primary)
- **Directory Picker Updates**:
  - Restricted browsing to petrophysics-workplace folder only
  - Changed UI from list view to 3-column grid layout
  - Added "New Folder" creation functionality
  - Implemented secure path validation to prevent directory traversal
  - Set default project path to petrophysics-workplace
  - Added right-click context menu with Rename and Delete options
  - Fixed folder name truncation with word wrapping (displays up to 2 lines)
  - **Integrated DirectoryPicker with File > Import menu**
  - **Integrated DirectoryPicker with Project > Open menu**
  - Fixed path display to show "petrophysics-workplace" at root
  - Server auto-creates petrophysics-workplace folder on first access

## Dependencies
- **Frontend**: React, Vite, Tailwind, Radix UI, Framer Motion, react-rnd, dnd-kit
- **Backend**: Express, tsx (dev runtime)
- **Database**: Drizzle ORM, @neondatabase/serverless (future use)
- **Build**: esbuild, TypeScript

## Running the Application
- **Development**: `npm run dev` (starts on port 5000)
- **Build**: `npm run build`
- **Production**: `npm start`
- **Database Push**: `npm run db:push` (when PostgreSQL configured)

## Deployment Configuration
- **Target**: Autoscale (stateless web application)
- **Build Command**: `npm run build`
- **Run Command**: `npm start`
- **Port**: 5000 (automatically set via PORT environment variable)
- **Storage**: File-based storage in `database/` directory persists across deployments

## User Preferences
- No specific preferences documented yet

## Notes
- Application uses file system for project storage in `database/` folder
- Well log data imported via CSV/LAS files through Feedback panel
- Projects are organized with standard folder structure (01-OUTPUT, 02-INPUT_LAS_FOLDER, etc.)
- Theme switching between light/dark mode available
