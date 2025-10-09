# Well Log Data Management Application

## Overview
A professional web-based application for managing and visualizing well log data in the oil and gas industry. The application features a multi-panel docking interface for viewing well logs, data browsers, zonation information, and feedback panels.

## Project Status
- **Status**: Successfully imported and configured for Replit environment
- **Last Updated**: October 9, 2025
- **Current State**: Fully functional with frontend and backend running

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
- Data browser with tabbed interface (Logs, Log Values, Constants)
- Project creation with standard folder structure
- Directory picker for navigating file systems
- Export functionality for data

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

### Project Management
- `POST /api/projects/create` - Create new project with standard folder structure
  - Body: `{ name: string, path: string }`
  - Returns: success status, project path, and created folders

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

### Host Configuration
- **Frontend (Vite)**: 0.0.0.0 with allowedHosts: true (required for Replit proxy)
- **Backend (Express)**: 0.0.0.0 for external access

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
- **October 9, 2025**: 
  - **Project Info Menu**: Added new menu in MenuBar displaying project details
    - Shows current project file path
    - Displays well count from Wells panel
    - Accessible from top menu bar
  - **CSV File Selector in Feedback Panel**: Replaced textarea with drag & drop CSV selector
    - Drag and drop CSV files directly into the panel
    - Click "Select CSV" button to browse files
    - Shows list of selected files with size and remove option
    - Visual feedback during drag operations
  - **Window Hover/Focus Effects**: Added visual feedback for window interaction
    - Border changes to primary color on hover/focus
    - Shadow effect appears when window is active
    - Smooth transitions for better UX
  - **Window Minimize/Maximize Feature**: Added bottom taskbar for managing minimized windows
    - Created BottomTaskbar component that displays minimized panels
    - Updated all panel components to support minimize/maximize functionality
    - Minimized panels are hidden from layout and shown in sticky bottom bar
    - Each minimized panel can be restored by clicking the maximize button
  - Initial import from GitHub
  - Configured for Replit environment
  - Updated vite.config.ts with host: "0.0.0.0" and allowedHosts: true
  - Verified application runs successfully on port 5000
  - Updated .gitignore to track replit.md

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
