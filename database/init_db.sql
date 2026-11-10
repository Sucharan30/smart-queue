-- ========================================================
-- Smart Queuing for Public Hospitals
-- Checkpoint 1: Database Initialization Script
-- ========================================================

-- Run this script using psql or pgAdmin:
-- psql -U postgres -f database/init_db.sql

-- 1. Create the Database if it doesn't already exist
-- (In psql, execute outside of a transaction block or directly via CREATE DATABASE)
CREATE DATABASE smart_queue_db;

-- Connect to the database
\c smart_queue_db;

-- 2. Grant permissions (optional if using default postgres user)
-- GRANT ALL PRIVILEGES ON DATABASE smart_queue_db TO postgres;

-- 3. Verification query
SELECT current_database(), current_user, version();

