-- 1. Crear la base de datos
CREATE DATABASE gdi_db;

-- 2. Crear el usuario con contraseña
CREATE USER gdi_user WITH PASSWORD 'gdi_password';

-- 3. Darle acceso a la base de datos
GRANT CONNECT ON DATABASE gdi_db TO gdi_user;

-- IMPORTANTE: Conéctate a la base de datos creada antes de seguir
-- Si estás en psql, usa:
-- \c gdi_db
\connect gdi_db;

-- 4. Crear las tablas
CREATE TABLE gdi_results (
    id SERIAL PRIMARY KEY,
    pilot TEXT NOT NULL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gdi_value FLOAT NOT NULL
);

CREATE TABLE gdi_contributions (
    id SERIAL PRIMARY KEY,
    gdi_result_id INTEGER NOT NULL REFERENCES gdi_results(id) ON DELETE CASCADE,
    indicator_name TEXT NOT NULL,
    hierarchy_level TEXT,
    impact_type TEXT,
    contribution FLOAT NOT NULL
);

-- 5. Dar permisos al usuario para trabajar con esas tablas
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO gdi_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO gdi_user;

-- 6. Permisos por defecto para futuras tablas (funciona bien desde PostgreSQL 9.0+)
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO gdi_user;
