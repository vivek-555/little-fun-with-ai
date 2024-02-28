DO
$do$
BEGIN
   IF EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'wiyseuser') THEN

      RAISE NOTICE 'Role "wiyseuser" already exists. Skipping.';
   ELSE
      CREATE ROLE wiyseuser LOGIN PASSWORD '12345';
   END IF;
END
$do$;
DO
$do$
BEGIN
   IF EXISTS (SELECT FROM pg_database WHERE datname = 'wiyse') THEN
      RAISE NOTICE 'Database already exists';
   ELSE
      PERFORM dblink_exec('dbname=' || current_database()  -- current db
                        , 'CREATE DATABASE wiyse');
   END IF;
END
$do$;
GRANT ALL PRIVILEGES ON DATABASE wiyse TO wiyseuser;
CREATE EXTENSION vector;