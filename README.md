### Poetry:

`pip install poetry`

### .env:

- DB_USERNAME=postgres
- DB_PASSWORD=postgres
- DB_NAME=ezred2db
- DB_HOST=localhost

### Generate init sql & restore

```
docker exec -i ezred2api-db pg_dump -U postgres --clean -d ezred2db > dump.sql
cat init.sql | docker exec -i ezred2api-db psql -U postgres -d ezred2db
```
