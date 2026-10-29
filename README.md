# Python E-commerce Products API

A REST API portfolio project built with **Python, FastAPI, SQLAlchemy, PostgreSQL, pytest, Docker, and GitHub Actions**.

## Features

- Create, retrieve, update, and delete products
- Pagination and filtering by category or product name
- Request validation with Pydantic
- Database uniqueness constraint for product SKUs
- API-key protection for write operations
- Automated API tests with pytest
- PostgreSQL environment with Docker Compose
- Continuous integration with GitHub Actions
- Interactive OpenAPI documentation at `/docs`

## Run with Docker

1. Copy `.env.example` to `.env`.
2. Set a strong, private `ADMIN_API_KEY` value.
3. Run:

```bash
docker compose up --build
```

Open http://localhost:8000/docs to explore the API.

## Local development

Requires Python 3.12 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
export ADMIN_API_KEY=local-dev-secret
uvicorn app.main:app --reload
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` and set the key with `$env:ADMIN_API_KEY="local-dev-secret"`.

When `DATABASE_URL` is not configured, the application uses a local SQLite database.

## API endpoints

| Method | Endpoint | Description | Requires API key |
| --- | --- | --- | --- |
| GET | `/health` | Basic health status | No |
| GET | `/products` | List products with pagination and filters | No |
| GET | `/products/{product_id}` | Get a product | No |
| POST | `/products` | Create a product | Yes |
| PATCH | `/products/{product_id}` | Update a product | Yes |
| DELETE | `/products/{product_id}` | Delete a product | Yes |

## Example requests

Create a product:

```bash
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -H "X-API-Key: local-dev-secret" \
  -d '{"sku":"KB-001","name":"Mechanical Keyboard","description":"Compact keyboard","price":"79.90","stock":25,"category":"Accessories"}'
```

List matching products:

```bash
curl "http://localhost:8000/products?category=Accessories&limit=20&offset=0"
```

Update stock:

```bash
curl -X PATCH http://localhost:8000/products/1 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: local-dev-secret" \
  -d '{"stock":30}'
```

## Run tests

```bash
pytest -q
```

The test suite covers CRUD behavior, duplicate SKUs, invalid input, authentication, pagination, filtering, and missing resources. Tests use an isolated SQLite database.

## Project structure

```text
app/
  __init__.py
  database.py
  models.py
  schemas.py
  main.py
tests/
  __init__.py
  conftest.py
  test_products.py
.github/workflows/ci.yml
Dockerfile
compose.yaml
requirements.txt
requirements-dev.txt
.env.example
```

## Design notes

- Offset pagination is simple and appropriate for this project; cursor pagination is worth considering for larger catalogs.
- Database tables are created at startup for easy local setup. Production deployments should use versioned database migrations.
- API-key authentication is a simplified demonstration. Production applications should use robust identity management and role-based access controls.
- SQLite-based tests are fast and portable. PostgreSQL integration tests would improve database-specific coverage.
- Docker Compose credentials are for local development only and must not be used in production.
- This project manages products only; it does not implement checkout, orders, or payment processing.

## License

MIT License. See [LICENSE](LICENSE).
