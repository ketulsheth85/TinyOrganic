psql -d template1 -c 'CREATE EXTENSION IF NOT EXISTS pgcrypto;'
psql -d $POSTGRES_DB -c 'CREATE EXTENSION IF NOT EXISTS pgcrypto;'
psql -d template1 -c 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'
psql -d $POSTGRES_DB -c 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'
psql -d template1 -c 'CREATE EXTENSION IF NOT EXISTS pg_trgm;'
psql -d $POSTGRES_DB -c 'CREATE EXTENSION IF NOT EXISTS pg_trgm;'
psql -d template1 -c 'CREATE EXTENSION IF NOT EXISTS btree_gin;'
psql -d $POSTGRES_DB -c 'CREATE EXTENSION IF NOT EXISTS btree_gin;'