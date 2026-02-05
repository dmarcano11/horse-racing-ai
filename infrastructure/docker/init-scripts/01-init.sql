-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS racing;
CREATE SCHEMA IF NOT EXISTS ml;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Set search path
ALTER DATABASE racing_db SET search_path TO racing, ml, analytics, public;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA racing TO racing_user;
GRANT ALL PRIVILEGES ON SCHEMA ml TO racing_user;
GRANT ALL PRIVILEGES ON SCHEMA analytics TO racing_user;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully!';
END $$;