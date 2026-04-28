-- ISP Software - Database Initialization
-- This script runs when PostgreSQL container first starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";    -- For fast text search
CREATE EXTENSION IF NOT EXISTS "btree_gin";  -- For GIN indexes

-- Set timezone
SET timezone = 'Asia/Dhaka';

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE ispdb TO ispuser;
