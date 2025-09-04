-- init.sql
CREATE USER task_user WITH PASSWORD 'task_pass';
CREATE DATABASE task_db OWNER task_user;
CREATE DATABASE task_test_db OWNER task_user;
GRANT ALL PRIVILEGES ON DATABASE task_db TO task_user;
GRANT ALL PRIVILEGES ON DATABASE task_test_db TO task_user;
