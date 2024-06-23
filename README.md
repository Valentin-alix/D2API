### Poetry:

`pip install poetry`

### .env:

- DB_USERNAME=postgres
- DB_PASSWORD=postgres
- DB_NAME=postgres
- DB_HOST=localhost

### Generate init sql & restore

```
docker exec -i ezred2db pg_dump -U postgres --data-only -d postgres > dump.sql
cat init.sql | docker exec -i postgres psql -U postgres -d postgres
```
