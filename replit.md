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

### Fresh GitHub Clone Setup
- ✅ **GitHub Import Completed Successfully** (Fresh Clone)
- ✅ Installed all npm dependencies (508 packages)
- ✅ Configured development workflow on port 5000
- ✅ Verified application runs correctly with all features working
- ✅ Configured deployment for production (autoscale deployment)
- ✅ Verified Vite configuration with allowedHosts: true for Replit proxy
- ✅ All panels functional: Wells, Well Log Plot, Data Browser, Zonation, Feedback
- ✅ Development server running on port 5000 with HMR (Hot Module Replacement)
- ✅ Backend and frontend integrated in single Express server

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
