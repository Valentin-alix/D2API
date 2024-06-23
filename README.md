### Poetry:

`pip install poetry`

### .env:

- DB_USERNAME=postgres
- DB_PASSWORD=postgres
- DB_NAME=ezred2db
- DB_HOST=localhost

### Generate init sql & dump datas

```
docker exec -i ezred2db pg_dump -U postgres --data-only -d ezred2db > dump.sql
bash scripts/populate.sh
```
