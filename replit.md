# Dockable Window Manager Application

## Overview

A professional petrophysics data analysis application featuring a dockable window management system inspired by modern IDEs. The application provides an interactive workspace for managing well logs, visualizing data through various plot types, and organizing geological zonation information. Built with React, TypeScript, and Express, it offers a sophisticated drag-and-drop interface for flexible panel arrangement with floating windows, docked layouts, and persistent workspace configurations.

## Recent Changes

### October 2025 - Replit Environment Setup & Enhancements
- **Environment Setup**: Successfully configured for Replit environment with Node.js and Python dependencies
- **File Preview Feature**: Enhanced Data Explorer with file preview functionality
  - Users can now single-click on files to view their contents in a preview dialog
  - Supports JSON formatting and text file display
  - Includes loading states and error handling
  - Visual indicators show which folders contain files
- **Flask-Based Backend Implementation** (Latest Update)
  - Converted Node.js backend logic to Flask for better Python integration
  - Flask server runs on port 5001, proxied through Express on port 5000
  - Modular Flask application structure with blueprints and utilities
  - **Data Models**: Well, Dataset, WellLog, Constant classes based on reference implementation
  - **Project Management Routes** (`/api/projects`):
    - POST `/create` - Create new project with folder structure
    - GET `/list` - List all projects
  - **Wells Management Routes** (`/api/wells`):
    - POST `/upload-las` - Upload and process LAS files
    - GET `/list` - List all wells in a project
    - GET `/<well_name>` - Get specific well data
    - GET `/` - Get all wells
  - **Visualization Routes** (`/api/visualization`):
    - POST `/well-log-plot` - Generate well log plots using matplotlib
    - POST `/cross-plot` - Generate cross plots with correlation analysis
    - GET `/log-data` - Get formatted log data for frontend visualization
  - **Utilities**:
    - `WellManager` - Handles well creation, loading, and LAS processing
    - `PlotGenerator` - Generates matplotlib plots (well logs and cross plots)
- **LAS File Processing System**: Integrated Flask-based well management system
  - Upload LAS files through API endpoints
  - Parse LAS files using lasio library
  - Create Well and Dataset objects with proper structure
  - Store well data as JSON in 10-WELLS folder (petrophysics-workplace structure)
  - Support for multiple datasets per well
  - Automatic well header and reference dataset creation
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