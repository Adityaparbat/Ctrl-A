# Overview

Inlightex is an accessibility-focused web application designed to empower disabled individuals through innovative technology solutions. The platform provides comprehensive assistive features including emergency support, reading assistance, social media integration, camera navigation, and welfare scheme guidance. The application emphasizes inclusivity by supporting multiple input methods including voice commands, Indian Sign Language (ISL), and traditional text input.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
The frontend is built using React 18 with TypeScript, leveraging modern development practices and accessibility-first design principles. The application uses Vite as the build tool for fast development and optimized production builds.

**UI Framework**: Utilizes shadcn/ui components built on top of Radix UI primitives, providing accessible and customizable components out of the box. The design system uses Tailwind CSS with a comprehensive theming system supporting both light and dark modes.

**State Management**: Implements TanStack Query (React Query) for server state management, providing efficient data fetching, caching, and synchronization capabilities. This choice ensures optimal performance for real-time accessibility features.

**Routing**: Uses Wouter for client-side routing, chosen for its lightweight footprint and simplicity, important for accessibility applications where performance matters.

**Animations**: Integrates Framer Motion for smooth, accessible animations that enhance user experience without compromising accessibility standards.

## Backend Architecture
The backend follows a RESTful API design using Express.js with TypeScript, structured for scalability and maintainability.

**Server Framework**: Express.js provides the core HTTP server functionality with custom middleware for request logging, error handling, and API route management.

**Development Setup**: The architecture supports hot module replacement in development through Vite integration while maintaining production optimization through esbuild bundling.

**Storage Interface**: Implements an abstracted storage interface (`IStorage`) with both in-memory and database implementations, allowing for flexible data persistence strategies.

## Data Storage Solutions
The application uses a hybrid approach to data management:

**Database**: PostgreSQL as the primary database, chosen for its robustness and excellent support for complex queries needed for accessibility features.

**ORM**: Drizzle ORM provides type-safe database operations with automatic TypeScript inference, reducing runtime errors and improving developer experience.

**Schema Management**: Uses Drizzle Kit for database migrations and schema management, with schemas defined in shared TypeScript files for consistency between frontend and backend.

**Session Management**: Implements PostgreSQL-backed session storage using connect-pg-simple for secure user session management.

## Authentication and Authorization
The current architecture establishes the foundation for user authentication with a comprehensive user schema including username and password fields. The session management infrastructure is in place using PostgreSQL-backed sessions, providing secure and scalable user authentication capabilities.

## External Dependencies

**Database**: Neon Database (@neondatabase/serverless) for managed PostgreSQL hosting with serverless capabilities, ensuring scalability for accessibility applications.

**UI Components**: Extensive use of Radix UI primitives for accessible component foundations, ensuring WCAG compliance across all interactive elements.

**Development Tools**: 
- Replit-specific plugins for development and debugging
- Font Awesome for iconography with accessibility considerations
- ESBuild for production bundling and optimization

**Styling**: 
- Tailwind CSS for utility-first styling
- PostCSS with Autoprefixer for browser compatibility
- Custom CSS variables for comprehensive theming support

The architecture prioritizes accessibility, performance, and scalability while maintaining a clear separation of concerns between frontend presentation, backend logic, and data persistence layers.