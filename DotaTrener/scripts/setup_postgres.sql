-- Run as PostgreSQL superuser (postgres), e.g. in pgAdmin Query Tool:
--   CREATE DATABASE / user for DotaTrener
--
-- Adjust password if you change DB_PASSWORD in .env

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'DotaTrener_user') THEN
        CREATE USER "DotaTrener_user" WITH PASSWORD '1234';
    ELSE
        ALTER USER "DotaTrener_user" WITH PASSWORD '1234';
    END IF;
END
$$;

SELECT 'CREATE DATABASE dotatrener_db OWNER "DotaTrener_user" ENCODING ''UTF8'' LC_COLLATE ''C'' LC_CTYPE ''C'' TEMPLATE template0'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'dotatrener_db')\gexec

GRANT ALL PRIVILEGES ON DATABASE dotatrener_db TO "DotaTrener_user";
