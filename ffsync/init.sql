CREATE DATABASE IF NOT EXISTS syncstorage_rs;
CREATE DATABASE IF NOT EXISTS tokenserver_rs;
GRANT ALL PRIVILEGES ON syncstorage_rs.* TO ffsync;
GRANT ALL PRIVILEGES ON tokenserver_rs.* TO ffsync;
