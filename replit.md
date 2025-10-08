# Dockable Window Manager Application

## Overview

A professional dockable window manager application for data analysis and project management. The system provides a flexible workspace with resizable panels, floating windows, and a tab-based interface inspired by modern IDEs like VS Code and Figma. Users can organize multiple data views (logs, wells, zonation, feedback) in a customizable layout with dark/light theme support.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Framework & Build System**
- **React 18** with TypeScript for type-safe component development
- **Vite** as the build tool and development server with HMR (Hot Module Replacement)
- **Wouter** for lightweight client-side routing
- **TanStack React Query** for server state management and data fetching

**UI Component System**
- **Shadcn/ui** component library built on Radix UI primitives for accessible, unstyled components
- **Tailwind CSS** for utility-first styling with custom design tokens
- **Class Variance Authority (CVA)** for managing component variants
- Design follows professional IDE patterns with dark mode as primary theme

**Window Management**
- Custom dockable panel system with floating window support using **react-rnd** for drag/resize
- Panel state management (visible/hidden, docked/floating, position, size) stored in component state
- Support for both grid-based docking and free-floating windows
- Persistent geometry tracking for floating panels

**Key UI Patterns**
- Tab-based navigation within panels
- Tree view for hierarchical data (wells, projects)
- Data grid with row selection for tabular data
- Context menus and dropdown menus for actions
- Toast notifications for user feedback

### Backend Architecture

**Server Framework**
- **Express.js** server with TypeScript
- Modular route registration system (`registerRoutes`)
- Middleware-based request logging with timing
- Custom error handling middleware

**Development Features**
- Vite integration in development mode with SSR template rendering
- Static file serving in production
- Request/response logging with JSON body capture (truncated at 80 chars)

**Storage Layer**
- Interface-based storage abstraction (`IStorage`)
- In-memory implementation (`MemStorage`) as default
- Designed for future database integration (Drizzle ORM configured)
- CRUD operations for user management

### Data Storage

**Database Configuration (Prepared but not fully implemented)**
- **Drizzle ORM** configured for PostgreSQL with Neon serverless
- Schema defined in `shared/schema.ts` with users table
- Zod schema validation for type-safe data operations
- Migration support via `drizzle-kit`

**Current State**
- Application uses in-memory storage via `MemStorage` class
- Database schema and configuration ready for activation
- Users table with UUID primary keys, username/password fields

### Design System

**Color Scheme**
- Dark mode primary with teal/cyan accents (#4A9FA8)
- Light mode with complementary palette
- CSS custom properties for theme switching
- Elevation system using transparent overlays for hover/active states

**Typography**
- **Inter** for UI text (300-700 weights)
- **JetBrains Mono** for monospace/data displays
- Consistent type scale (11px-14px for UI elements)

**Layout Principles**
- Minimum panel width: 280px, default 320-400px
- 4px resize handles with 1px visible dividers
- Consistent spacing using Tailwind scale (1-8 units)
- Rounded corners: 4px panels, 2px tabs

## External Dependencies

### Core Dependencies
- **@neondatabase/serverless** - Neon Postgres serverless driver
- **drizzle-orm** - TypeScript ORM with Zod integration
- **@tanstack/react-query** - Server state management
- **react-rnd** - Resizable and draggable components
- **react-mosaic-component** - Grid-based window tiling (appears in DockManager but may be replaced)

### UI Component Libraries
- **@radix-ui/** - Comprehensive set of accessible UI primitives (accordion, dialog, dropdown, popover, tabs, tooltip, etc.)
- **cmdk** - Command palette component
- **embla-carousel-react** - Carousel/slider functionality
- **lucide-react** - Icon library
- **vaul** - Drawer component

### Development Tools
- **Replit-specific plugins** - Runtime error overlay, cartographer, dev banner
- **PostCSS** with Autoprefixer for CSS processing
- **esbuild** for server bundling in production

### Styling & Utilities
- **tailwindcss** - Utility-first CSS framework
- **class-variance-authority** - Component variant management
- **clsx** / **tailwind-merge** - Class name utilities
- **date-fns** - Date manipulation library

### Session & Authentication (Configured)
- **connect-pg-simple** - PostgreSQL session store (not actively used)
- User schema prepared with username/password fields