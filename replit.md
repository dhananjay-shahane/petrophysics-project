# Dockable Window Manager Application

## Overview
A professional petrophysics data analysis application featuring a dockable window management system inspired by modern IDEs. The application provides an interactive workspace for managing well logs, visualizing data through various plot types, and organizing geological zonation information. Built with React, TypeScript, and Flask, it offers a sophisticated drag-and-drop interface for flexible panel arrangement with floating windows, docked layouts, and persistent workspace configurations. The project aims to provide a robust, modern tool for petrophysical data analysis with a focus on user experience and data integrity.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### UI/UX Decisions
The application features a modern IDE-like interface with a dockable window management system for flexible panel arrangement (floating, docked, minimized, maximized). It uses a dark mode theme with a custom color palette (deep slate backgrounds, teal/cyan accents) and the Inter/JetBrains Mono font families. The design system is based on Tailwind CSS with custom design tokens, leveraging `shadcn/ui` for accessible components. Real-time feedback and clear error messages are provided during operations like LAS file uploads.

### Technical Implementations
**Frontend:**
- **Framework:** React with TypeScript, using Vite as the build tool.
- **State Management:** Local component state with React hooks; no global state management library is currently used.
- **Window Management:** `@dnd-kit` for drag-and-drop, `react-rnd` for resizable and draggable floating windows.
- **Data Visualization:** `Recharts` for cross-plots, log plots, and well log visualization.
- **UI Components:** Utilizes `Radix UI` primitives and `shadcn/ui` components.
- **Routing:** `wouter` for client-side routing.
- **Data Fetching:** `@tanstack/react-query` for server state management.

**Backend:**
- **Primary Server:** Flask, serving both the static frontend assets (in production) and the API.
- **Language:** Python, with Flask-CORS enabled.
- **API Structure:** RESTful endpoints under `/api` for project management, well handling, and visualization.
- **File Processing:** `lasio` library for LAS file parsing, `matplotlib`, `NumPy`, and `Pandas` for data processing and plot generation.
- **Well Data Model:** Custom Python classes (`Well`, `Dataset`, `WellLog`, `Constant`) for representing well data, with serialization/deserialization to JSON (`.ptrc` files).
- **Project Structure:** Automated creation of a standard petrophysics folder structure within projects.

### Feature Specifications
- **LAS File Processing:** Direct upload, parsing, and conversion of LAS files into structured Well objects. Supports real-time preview and detailed logging during upload.
- **Well Management:** Wells are saved as `.ptrc` (Petrophysics Resource Container) JSON files in a dedicated project folder (`10-WELLS`).
- **Project Management:** Users can create new projects with a predefined folder structure for organizing petrophysical data.
- **Data Visualization:** Generation of various plot types (cross-plots, log plots) from well data.
- **File Preview:** Enhanced Data Explorer allows single-click preview of file contents (JSON, text).
- **Python Logging Panel:** A dedicated panel for real-time, color-coded logs from backend Python processes.

### System Design Choices
- **Development Environment:** Frontend (Vite) runs on port 5000, Backend (Flask) runs on port 5001. Vite proxies `/api/*` requests to Flask.
- **Production Environment:** Flask serves both the static frontend (`dist` folder) and API on port 5000.
- **Data Persistence:** Well data is stored as `.ptrc` JSON files directly in the filesystem. Project-related files are also file-based.
- **Cross-Platform Compatibility:** Path handling fixed to support Windows, Mac, and Linux paths.
- **Containerization:** Configured for VM deployment with an always-running server.

## External Dependencies
- **UI Libraries:** `Radix UI`, `@dnd-kit`, `react-rnd`, `shadcn/ui`, `cmdk`.
- **Charting:** `Recharts`.
- **Python Libraries:** `Flask`, `lasio`, `matplotlib`, `NumPy`, `Pandas`, `werkzeug`.
- **Development Tools:** `Vite`, `TypeScript`, `Tailwind CSS`, `PostCSS`, `Autoprefixer`, `tsx`, `esbuild`, `uv` (package manager).
- **Routing:** `wouter`.
- **Data Fetching:** `@tanstack/react-query`.
- **File Parsing:** `csv-parse`.
- **Database (Planned/Configured but not active):** `Drizzle ORM`, `drizzle-kit`, `@neondatabase/serverless` (for PostgreSQL).