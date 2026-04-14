-- init.sql
-- Crear usuario específico para Django
CREATE USER django_app_user WITH PASSWORD 'passwordseguradjango';

-- Darle todos los privilegios sobre la base de datos
GRANT ALL PRIVILEGES ON DATABASE mi_proyecto TO django_app_user;

-- Conectarse a la base de datos para permisos en el esquema public
\c mi_proyecto;

-- Permisos en el esquema public (tablas, secuencias, funciones)
GRANT ALL ON SCHEMA public TO django_app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO django_app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO django_app_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO django_app_user;

-- Permisos por defecto para objetos futuros
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO django_app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO django_app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO django_app_user;