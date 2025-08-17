# Database Initialization System

## Overview

The database initialization system has been completely redesigned to provide robust, automatic database and table creation with proper error handling and timezone compatibility. This system ensures that the application can start successfully regardless of the initial database state.

## Key Features

### Automatic Database Creation
- **Smart Detection**: Automatically detects if the `raffles_db` database exists
- **Graceful Creation**: Creates the database if it doesn't exist using appropriate permissions
- **Environment Awareness**: Handles both local development and production environments differently

### Composite Primary Key Support
- **User Isolation**: All entities use composite primary keys that include `user_id`
- **Hierarchical Structure**: Maintains proper relationships between users, projects, raffle sets, and raffles
- **Auto-increment Scoping**: Each user has their own numbering sequence starting from 1

### Robust Error Handling
- **Connection Recovery**: Handles "Unknown database" errors gracefully
- **Multiple Strategies**: Falls back between SQLAlchemy and raw SQL methods
- **Detailed Logging**: Provides clear error messages and success confirmations

## Implementation Details

### Database Creation Flow

```python
def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    if settings.DATABASE_URL or settings.MYSQL_URL:
        # Railway environment - database should already exist
        return True
    
    # Connect to MySQL server without specifying database
    sys_engine = create_engine(f"mysql+pymysql://{settings.MARIADB_USERNAME}:{settings.MARIADB_PASSWORD}@{settings.MARIADB_SERVER}:{settings.MARIADB_PORT}")
    
    with sys_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.MARIADB_DATABASE}"))
        return True
```

### Table Creation Strategy

1. **Primary Method**: SQLAlchemy metadata creation
2. **Fallback Method**: Raw SQL execution from structure.sql
3. **Verification**: Always verifies that all required tables exist

### Startup Integration

The system integrates seamlessly with FastAPI startup:

```python
# In database/__init__.py
try:
    if create_database_if_not_exists():
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully")
except Exception as e:
    print(f"Warning: Could not create database/tables: {e}")
```

## Environment Support

### Local Development
- Creates database and user if they don't exist
- Handles MariaDB/MySQL setup automatically
- Provides detailed error messages for troubleshooting

### Production/Railway
- Skips database creation (assumes managed database)
- Uses provided connection strings directly
- Optimized for cloud deployment environments

## Benefits

### Developer Experience
- **Zero Configuration**: Works out of the box after cloning
- **Clear Feedback**: Detailed logging shows exactly what's happening
- **Resilient Startup**: Application starts even if database needs initialization

### Production Reliability
- **Graceful Degradation**: Continues operation even with initialization warnings
- **Environment Detection**: Automatically adapts to deployment environment
- **Connection Pooling**: Maintains efficient database connections

### Maintenance
- **Self-Healing**: Automatically fixes missing databases/tables
- **Documented Process**: Clear separation between creation and connection logic
- **Testable Components**: Each function has a single, clear responsibility

## Related Components

- **JWT Token System**: Fixed timezone issues for proper token validation
- **Composite Primary Keys**: Enables user isolation and predictable numbering
- **Universal Helper Functions**: Streamlined database operations across all models
