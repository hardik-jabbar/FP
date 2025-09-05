-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set timezone to UTC
SET TIMEZONE='UTC';

-- Create additional roles if needed
-- CREATE ROLE readonly NOINHERIT LOGIN PASSWORD 'readonly';
-- GRANT CONNECT ON DATABASE farmpower TO readonly;
-- GRANT USAGE ON SCHEMA public TO readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly;

-- Set default statement timeout for all sessions (30 seconds)
ALTER DATABASE farmpower SET statement_timeout = '30s';

-- Set default lock timeout (10 seconds)
ALTER DATABASE farmpower SET lock_timeout = '10s';

-- Set default idle in transaction session timeout (10 minutes)
ALTER DATABASE farmpower SET idle_in_transaction_session_timeout = '10min';

-- Optimize database settings for development
ALTER SYSTEM SET shared_buffers = '512MB';
ALTER SYSTEM SET effective_cache_size = '2GB';
ALTER SYSTEM SET maintenance_work_mem = '256MB';
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET max_parallel_workers_per_gather = '2';

-- Log all statements (for development only)
ALTER SYSTEM SET log_statement = 'all';

-- Force password encryption
ALTER SYSTEM SET password_encryption = 'scram-sha-256';

-- Reload configuration
SELECT pg_reload_conf();

-- Create additional schemas if needed
-- CREATE SCHEMA IF NOT EXISTS auth;
-- CREATE SCHEMA IF NOT EXISTS storage;

-- Set default privileges for future objects
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO postgres;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO postgres;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO postgres;

-- Create a read-only user for monitoring
-- CREATE USER monitor WITH PASSWORD 'monitor_password';
-- GRANT pg_monitor TO monitor;

-- Create a role for application access
-- CREATE ROLE app_user NOINHERIT LOGIN PASSWORD 'app_password';
-- GRANT CONNECT ON DATABASE farmpower TO app_user;
-- GRANT USAGE ON SCHEMA public TO app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO app_user;

-- Create a role for migrations
-- CREATE ROLE migration_user NOINHERIT LOGIN PASSWORD 'migration_password' SUPERUSER;

-- Create a role for backups
-- CREATE ROLE backup_user NOINHERIT LOGIN PASSWORD 'backup_password';
-- GRANT CONNECT ON DATABASE farmpower TO backup_user;
-- GRANT USAGE ON SCHEMA public TO backup_user;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO backup_user;

-- Create a role for read replicas
-- CREATE ROLE replica_user WITH REPLICATION PASSWORD 'replica_password' LOGIN;

-- Create publication for logical replication
-- CREATE PUBLICATION dbz_publication FOR ALL TABLES;
-- ALTER PUBLICATION dbz_publication OWNER TO postgres;

-- Create replication slot
-- SELECT * FROM pg_create_physical_replication_slot('replication_slot');

-- Create a role for monitoring
-- CREATE ROLE monitoring WITH LOGIN PASSWORD 'monitoring_password';
-- GRANT pg_monitor TO monitoring;

-- Create a role for read-only access to specific tables
-- CREATE ROLE reporting_user WITH LOGIN PASSWORD 'reporting_password';
-- GRANT CONNECT ON DATABASE farmpower TO reporting_user;
-- GRANT USAGE ON SCHEMA public TO reporting_user;
-- GRANT SELECT ON TABLE users, orders TO reporting_user; -- Add specific tables

-- Set up row-level security if needed
-- ALTER TABLE your_table ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY user_policy ON your_table FOR ALL TO app_user USING (owner = current_user);

-- Create a role for database maintenance
-- CREATE ROLE maintenance_user WITH LOGIN PASSWORD 'maintenance_password';
-- GRANT pg_signal_backend TO maintenance_user;

-- Create a role for connection pooling
-- CREATE ROLE pooler WITH LOGIN PASSWORD 'pooler_password';
-- GRANT CONNECT ON DATABASE farmpower TO pooler;

-- Create a role for schema migrations
-- CREATE ROLE migrator WITH LOGIN PASSWORD 'migrator_password' CREATEDB CREATEROLE;

-- Create a role for data loading/ETL
-- CREATE ROLE etl_user WITH LOGIN PASSWORD 'etl_password';
-- GRANT CONNECT ON DATABASE farmpower TO etl_user;
-- GRANT USAGE ON SCHEMA public TO etl_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA public TO etl_user;
-- GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO etl_user;

-- Create a role for analytics
-- CREATE ROLE analytics_user WITH LOGIN PASSWORD 'analytics_password';
-- GRANT CONNECT ON DATABASE farmpower TO analytics_user;
-- GRANT USAGE ON SCHEMA public TO analytics_user;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analytics_user;

-- Create a role for API access
-- CREATE ROLE api_user WITH LOGIN PASSWORD 'api_password';
-- GRANT CONNECT ON DATABASE farmpower TO api_user;
-- GRANT USAGE ON SCHEMA public TO api_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO api_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO api_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO api_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO api_user;

-- Create a role for background workers
-- CREATE ROLE worker_user WITH LOGIN PASSWORD 'worker_password';
-- GRANT CONNECT ON DATABASE farmpower TO worker_user;
-- GRANT USAGE ON SCHEMA public TO worker_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO worker_user;
-- GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO worker_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO worker_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO worker_user;

-- Create a role for read replicas with specific privileges
-- CREATE ROLE replica_reader WITH LOGIN PASSWORD 'replica_reader_password';
-- GRANT CONNECT ON DATABASE farmpower TO replica_reader;
-- GRANT TEMPORARY ON DATABASE farmpower TO replica_reader;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO replica_reader;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO replica_reader;

-- Create a role for database administrators
-- CREATE ROLE dba WITH SUPERUSER CREATEDB CREATEROLE REPLICATION BYPASSRLS LOGIN PASSWORD 'dba_password';

-- Create a role for application administrators
-- CREATE ROLE app_admin WITH CREATEDB CREATEROLE LOGIN PASSWORD 'app_admin_password';
-- GRANT CONNECT ON DATABASE farmpower TO app_admin;
-- GRANT ALL PRIVILEGES ON DATABASE farmpower TO app_admin;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_admin;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_admin;
-- GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO app_admin;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO app_admin;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO app_admin;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON FUNCTIONS TO app_admin;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TYPES TO app_admin;

-- Create a role for read-only access to specific columns
-- CREATE ROLE hr_user WITH LOGIN PASSWORD 'hr_password';
-- GRANT CONNECT ON DATABASE farmpower TO hr_user;
-- GRANT USAGE ON SCHEMA public TO hr_user;
-- GRANT SELECT (id, name, email, department) ON employees TO hr_user;

-- Create a role for write access to specific tables
-- CREATE ROLE order_processor WITH LOGIN PASSWORD 'order_processor_password';
-- GRANT CONNECT ON DATABASE farmpower TO order_processor;
-- GRANT USAGE ON SCHEMA public TO order_processor;
-- GRANT SELECT, INSERT, UPDATE ON orders, order_items TO order_processor;
-- GRANT USAGE, SELECT ON SEQUENCE orders_id_seq, order_items_id_seq TO order_processor;

-- Create a role for read access to materialized views
-- CREATE ROLE report_viewer WITH LOGIN PASSWORD 'report_viewer_password';
-- GRANT CONNECT ON DATABASE farmpower TO report_viewer;
-- GRANT USAGE ON SCHEMA public TO report_viewer;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO report_viewer;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO report_viewer;

-- Create a role for ETL processes
-- CREATE ROLE etl_processor WITH LOGIN PASSWORD 'etl_processor_password';
-- GRANT CONNECT ON DATABASE farmpower TO etl_processor;
-- GRANT USAGE ON SCHEMA public, staging, warehouse TO etl_processor;
-- GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA public, staging, warehouse TO etl_processor;
-- GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public, staging, warehouse TO etl_processor;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public, staging, warehouse GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLES TO etl_processor;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public, staging, warehouse GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO etl_processor;

-- Create a role for API access with read-only to specific tables
-- CREATE ROLE api_reader WITH LOGIN PASSWORD 'api_reader_password';
-- GRANT CONNECT ON DATABASE farmpower TO api_reader;
-- GRANT USAGE ON SCHEMA public TO api_reader;
-- GRANT SELECT ON products, categories, inventory TO api_reader;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO api_reader;

-- Create a role for API access with write access to specific tables
-- CREATE ROLE api_writer WITH LOGIN PASSWORD 'api_writer_password';
-- GRANT CONNECT ON DATABASE farmpower TO api_writer;
-- GRANT USAGE ON SCHEMA public TO api_writer;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON orders, order_items, customers TO api_writer;
-- GRANT USAGE, SELECT, UPDATE ON SEQUENCE orders_id_seq, order_items_id_seq, customers_id_seq TO api_writer;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO api_writer;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO api_writer;
