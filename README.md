## Run
1) `docker compose up -d`
2) `docker compose exec -T dbms1 sh -lc 'psql -U ddbs -d ddbs1 -v ON_ERROR_STOP=1 -f -' < sql/schema.sql`
   `docker compose exec -T dbms2 sh -lc 'psql -U ddbs -d ddbs2 -v ON_ERROR_STOP=1 -f -' < sql/schema.sql`
3) `uv run -- uvicorn services.api.app.main:app --reload` → GET /health
