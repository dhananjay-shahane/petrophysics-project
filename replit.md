# Well Log Data Management Application

## Overview
A professional web-based application for managing and visualizing well log data in the oil and gas industry. The application features a multi-panel docking interface for viewing well logs, data browsers, zonation information, and feedback panels.

## Project Status
- **Status**: Successfully imported and configured for Replit environment
- **Last Updated**: October 9, 2025 (Fresh import setup completed)
- **Current State**: Fully functional with frontend and backend running on port 5000

## Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 5
- **UI Components**: Radix UI component library
- **Styling**: Tailwind CSS with custom animations
- **State Management**: TanStack React Query
- **Routing**: Wouter
- **Layout**: Advanced docking system with react-mosaic-component, react-resizable-panels, and react-rnd

### Backend
- **Runtime**: Node.js with TypeScript
- **Framework**: Express.js
- **Database ORM**: Drizzle ORM (configured for PostgreSQL)
- **Session Management**: express-session with connect-pg-simple (when database is connected)
- **Authentication**: Passport.js with local strategy
- **WebSocket**: ws library for real-time features

### Development Tools
- **Package Manager**: npm
- **TypeScript Compiler**: tsx for development, esbuild for production builds
- **Database Migrations**: drizzle-kit

## Project Structure

```
.
├── client/              # Frontend React application
│   ├── src/
│   │   ├── components/  # React components
│   │   │   ├── ui/      # Radix UI component wrappers
│   │   │   └── examples/
│   │   ├── pages/       # Page components
│   │   ├── hooks/       # Custom React hooks
│   │   └── lib/         # Utilities and query client
│   └── index.html       # HTML entry point
├── server/              # Backend Express application
│   ├── index.ts         # Main server entry point
│   ├── routes.ts        # API route definitions
│   ├── storage.ts       # Data storage abstraction
│   └── vite.ts          # Vite dev server integration
├── shared/              # Shared types and schemas
│   └── schema.ts        # Database schema definitions
├── migrations/          # Database migration files
├── dist/                # Production build output
├── vite.config.ts       # Vite configuration
├── drizzle.config.ts    # Drizzle ORM configuration
└── tsconfig.json        # TypeScript configuration
```

## Key Features

### Well Log Visualization
- Interactive well log plotting with multiple tracks
- Support for various log types (Gamma Ray, Deep Resistivity, PhiT, Sw, etc.)
- Customizable plot panels with zoom and pan capabilities

### Data Management
- **ProjectInfoBar**: Top bar displaying project name, file path, and well count with visual icons
- **CSV/LAS File Loading**: 
  - Drag & drop or file selection in Feedback panel
  - Case-insensitive file extension validation (.CSV, .csv, .LAS, .las)
  - Automatic parsing and population of Wells panel
  - CSV parser: Extracts headers and rows as structured data
  - LAS parser: Parses "MNEM.UNIT VALUE : DESCRIPTION" format with wellInfo dictionary
- **Project Persistence**:
  - Save project data to database folder as JSON (includes wells, path, timestamps)
  - Load saved projects via dialog with project list
  - Database folder tracked in version control
- Data browser with tabbed interface (Logs, Log Values, Constants)
- Project creation with standard folder structure
- Directory picker for navigating file systems
- Project folder selection from Open menu

### User Interface
- Advanced docking workspace with draggable and resizable panels
- Multiple panel types: Wells, Well Log Plot, Data Browser, Zonation, Feedback
- **Window Management with Bottom Taskbar**:
  - Minimize any panel by clicking the minimize button (—) in the panel header
  - Minimized panels are removed from the layout and appear in a sticky bottom taskbar
  - Each minimized panel shows as a button with its title and a maximize icon
  - Click the maximize button to restore the panel to its previous position
  - The bottom taskbar automatically appears when panels are minimized and hides when empty
- Dark/light theme support via next-themes
- Responsive menu bar with dropdown menus

### Project Organization
Standard project structure created with folders:
- 01-OUTPUT
- 02-INPUT_LAS_FOLDER
- 03-DEVIATION
- 04-WELL_HEADER
- 05-TOPS_FOLDER
- 06-ZONES_FOLDER
- 07-DATA_EXPORTS
- 08-VOL_MODELS
- 09-SPECS
- 10-WELLS

## API Endpoints

### Directory Management
- `GET /api/directories/list?path={path}` - List directories at specified path
  - Returns: currentPath, parentPath, and array of directories
  - Gracefully handles missing directories (returns parent path with empty directories array)

### Project Management
- `POST /api/projects/create` - Create new project with standard folder structure
  - Body: `{ name: string, path: string }`
  - Returns: success status, project path, and created folders

- `POST /api/projects/save` - Save project data to database folder as JSON
  - Body: `{ projectData: ProjectData }`
  - Saves to: database/ProjectName_timestamp.json
  - Returns: success status, filePath, fileName

- `GET /api/projects/load/:fileName` - Load project from database folder
  - Returns: success status and projectData object

- `GET /api/projects/list` - List all saved projects
  - Returns: success status and array of project metadata (fileName, name, path, wellCount, createdAt, updatedAt)

## Database Schema

### Users Table
```typescript
{
  id: varchar (UUID primary key)
  username: text (unique, not null)
  password: text (not null)
}
```

Note: Currently using in-memory storage (MemStorage). To enable PostgreSQL:
1. Create a PostgreSQL database in Replit
2. The DATABASE_URL environment variable will be automatically set
3. Run `npm run db:push` to create tables
4. Update server/storage.ts to use database storage instead of MemStorage

## Environment Configuration

### Port Configuration
- **Development & Production**: Port 5000 (required by Replit)
- Frontend dev server runs through Vite middleware on the same port
- Backend API routes prefixed with `/api`
- Server configured to bind to 0.0.0.0:5000 for external access

### Host Configuration
- **Frontend (Vite)**: 0.0.0.0 with allowedHosts: true (required for Replit proxy)
- **Backend (Express)**: 0.0.0.0 for external access

### Deployment Configuration
- **Target**: VM (always-on server for full-stack application)
- **Build Command**: `npm run build` (builds both frontend and backend)
- **Run Command**: `npm start` (runs production server from dist/)
- **Port**: 5000 (same as development)

## Development Workflow

### Running the Application
```bash
npm run dev      # Start development server (frontend + backend)
npm run build    # Build for production
npm run start    # Start production server
npm run check    # Type check with TypeScript
npm run db:push  # Push database schema changes
```

### Development Server
The `npm run dev` command starts:
1. Express server with Vite middleware integration
2. Hot module replacement (HMR) for React components
3. API server on `/api/*` routes
4. Vite dev server serving the frontend

### Vite Integration
In development mode, the Express server uses Vite's middleware mode to:
- Serve the frontend with hot reload
- Transform TypeScript and JSX on the fly
- Provide error overlays for runtime errors
- Support Replit-specific development plugins

## Replit-Specific Configuration

### Vite Plugins (Development Only)
- `@replit/vite-plugin-runtime-error-modal` - Error overlay for runtime errors
- `@replit/vite-plugin-cartographer` - Code navigation helper
- `@replit/vite-plugin-dev-banner` - Development banner

### Important Settings
- Host set to 0.0.0.0 for external access
- allowedHosts: true to work with Replit's proxy/iframe
- Port 5000 is the only non-firewalled port

## User Preferences
None specified yet.

## Recent Changes
- **October 9, 2025 (Latest Session - Complete Project Persistence)**:
  - **ProjectInfoBar Component**: Created dedicated top bar component
    - Displays project name, file path, and well count with folder/file icons
    - Replaced Project Info dropdown menu in MenuBar
  - **CSV/LAS File Loading System**: Complete implementation
    - Case-insensitive file validation (.CSV, .csv, .LAS, .las)
    - Drag & drop and file selection in Feedback panel
    - "Load Log" button triggers parsing and updates Wells panel
    - CSV Parser: Extracts headers and rows as structured data
    - LAS Parser: Correctly parses "MNEM.UNIT VALUE : DESCRIPTION" format
    - Error handling with toast notifications
  - **Project Folder Selection**: Open menu option to select project folder
    - Auto-updates project name and path from selected folder
  - **Complete Server-Side Persistence**: End-to-end save/load workflow
    - Backend API endpoints for save, load, and list projects
    - Projects saved to database/ folder as JSON with timestamps
    - ProjectListDialog for browsing and loading saved projects
    - Full state hydration including wells data
    - Toast notifications for save/load success/error
    - Database folder tracked in version control (.gitignore updated)
  - **API Improvements**: 
    - Fixed directory listing to gracefully handle ENOENT errors
    - Returns parent path with empty directories array when path doesn't exist
- **October 9, 2025 (Fresh Import)**:
  - Installed all npm dependencies (508 packages)
  - Fixed server configuration to use port 5000 and bind to 0.0.0.0
  - Updated .gitignore to explicitly track replit.md
  - Configured workflow to run `npm run dev` on port 5000
  - Set up deployment configuration (VM target with build and run commands)
  - Verified application runs successfully with all panels rendering correctly
- **October 9, 2025 (Previous session)**: 
  - Window Hover/Focus Effects with border and shadow
  - Window Minimize/Maximize Feature with bottom taskbar
  - Initial import from GitHub and Replit environment configuration

## Architecture Decisions

### Storage Layer
- **Current**: In-memory storage using MemStorage class
- **Future**: PostgreSQL with Drizzle ORM when database is provisioned
- Storage interface (IStorage) provides abstraction for easy migration

### Session Management
- express-session with memory store (development)
- connect-pg-simple ready for PostgreSQL sessions (production)

### Build Strategy
- Frontend: Vite builds to `dist/public`
- Backend: esbuild bundles server code to `dist`
- Single production command serves both static files and API

## Security Considerations
- Path traversal protection in project creation endpoint
- Project names validated against regex pattern
- Passwords should be hashed before storage (implement bcrypt)
- HTTPS recommended for production deployment

## Next Steps / TODO
1. Implement PostgreSQL storage layer to replace MemStorage
2. Add authentication endpoints (login, register, logout)
3. Implement password hashing with bcrypt
4. Add file upload functionality for LAS files
5. Create well log parsing and visualization logic
6. Add real-time collaboration features using WebSocket
7. Implement data export functionality
8. Add unit and integration tests
