# Dockable Window Manager Application

## Overview

A professional petrophysics data analysis application featuring a dockable window management system inspired by modern IDEs. The application provides an interactive workspace for managing well logs, visualizing data through various plot types, and organizing geological zonation information. Built with React, TypeScript, and Express, it offers a sophisticated drag-and-drop interface for flexible panel arrangement with floating windows, docked layouts, and persistent workspace configurations.

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
- Python matplotlib integration via server-side plot generation
- Dynamic data binding from well data to chart components

**UI Design System**
- Tailwind CSS with custom design tokens
- Dark mode support with CSS variables
- Theme: "new-york" style from shadcn/ui
- Custom color palette: deep slate backgrounds, teal/cyan accents
- Typography: Inter font family with JetBrains Mono for data displays

### Backend Architecture

**Server Framework**
- Express.js with TypeScript
- ESM module system (type: "module")
- Development: tsx for hot reloading
- Production: esbuild for bundling

**API Structure**
- RESTful endpoints under `/api` namespace
- File upload handling with multer middleware
- LAS (Log ASCII Standard) and CSV file parsing
- Project management: CRUD operations for projects and wells
- Python integration for matplotlib plot generation

**File Processing Pipeline**
1. File upload via multipart/form-data
2. Parse LAS files to extract well information and curve data
3. Parse CSV files using csv-parse/sync
4. Store parsed data in memory (MemStorage)
5. Generate visualization plots on-demand

**Session & Storage**
- In-memory storage implementation (MemStorage class)
- Session management with connect-pg-simple (configured for PostgreSQL)
- Static file serving from public directory for generated plots

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