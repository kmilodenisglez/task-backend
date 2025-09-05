#!/bin/bash
echo "🗑️  Dropping and recreating PostgreSQL schema..."

podman exec -i my_postgres psql -U task_user -d task_db << EOF
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO task_user;
GRANT ALL ON SCHEMA public TO PUBLIC;
EOF

echo "✅ Database schema reset successfully"

# Aplicar migraciones
alembic upgrade head

echo "🔄 Migrations applied"