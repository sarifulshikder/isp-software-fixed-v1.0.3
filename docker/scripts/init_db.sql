-- =============================================================================
-- ISP Management Software - Database Initialization (Fixed v1.0.3)
-- Fix: Create role BEFORE granting privileges
-- =============================================================================

-- Create user if not exists (prevents error on re-deploy)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ispuser') THEN
        CREATE USER ispuser WITH PASSWORD 'isppassword';
    END IF;
END
$$;

-- Create database if not exists
SELECT 'CREATE DATABASE ispdb OWNER ispuser'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ispdb')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ispdb TO ispuser;

-- Connect to ispdb and setup extensions
\c ispdb

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO ispuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ispuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ispuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ispuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ispuser;

-- Enable useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";