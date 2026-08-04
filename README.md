# Module 14 Calculation BREAD Project

This is my Module 14 FastAPI project. It adds complete BREAD functionality for calculations: Browse, Read, Edit, Add, and Delete. Calculations are connected to the logged-in user through JWT authentication.

## Features

- FastAPI backend
- SQLAlchemy User and Calculation models
- Pydantic validation schemas
- Secure password hashing
- JWT login and registration
- User-specific calculation BREAD routes
- Browser pages for register, login, and calculations
- Client-side validation for calculation inputs
- Unit, integration, and Playwright E2E tests
- GitHub Actions CI/CD with Docker build, scan, and Docker Hub push

## Project Files

- `main.py` has the FastAPI app and routes.
- `app/security.py` has password hashing, password verification, JWT creation, and JWT decoding.
- `app/schemas.py` has Pydantic schemas for users, auth, and calculations.
- `app/models.py` has the SQLAlchemy models.
- `app/crud.py` has database helper functions.
- `static/register.html` has the registration page.
- `static/login.html` has the login page.
- `static/calculations.html` has the calculation BREAD page.
- `static/auth.js` handles login/register browser logic.
- `static/calculations.js` handles calculation Browse, Read, Edit, Add, and Delete actions.
- `tests/integration` has API integration tests.
- `tests/e2e` has Playwright browser tests.
- `.github/workflows/ci-cd.yml` runs tests, builds Docker, scans the image, and pushes to Docker Hub.

## Run Locally

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Run the application:

```powershell
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Useful pages:

```text
http://127.0.0.1:8000/static/register.html
http://127.0.0.1:8000/static/login.html
http://127.0.0.1:8000/static/calculations.html
http://127.0.0.1:8000/docs
```

## Manual Checks

1. Register a user on `/static/register.html`.
2. Go to `/static/calculations.html`.
3. Add a calculation.
4. Click Read to view calculation details.
5. Click Edit, change values, and update the calculation.
6. Click Delete to remove the calculation.

## Run Tests

Run all tests:

```powershell
pytest
```

Run only Playwright E2E tests:

```powershell
pytest tests/e2e
```

## Run With Docker Compose

```powershell
docker compose up --build
```

FastAPI:

```text
http://localhost:8000
```

pgAdmin:

```text
http://localhost:5050
```

## Main API Endpoints

JWT authentication:

```text
POST /register
POST /login
```

Calculation BREAD routes:

```text
GET /calculations
GET /calculations/{id}
POST /calculations
PUT /calculations/{id}
DELETE /calculations/{id}
```

Calculation example:

```json
{
  "a": 15,
  "b": 3,
  "type": "Divide"
}
```

The calculation routes require this header:

```text
Authorization: Bearer your-jwt-token
```

## Docker Hub

Docker Hub repository:

```text
https://hub.docker.com/r/kp949/module14-calculation-bread
```

## GitHub Actions Secrets

Add these repository secrets in GitHub:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

The Docker Hub token should have read and write access.

## Submission Screenshots

For Canvas, include:

- GitHub repository link
- Screenshot of successful GitHub Actions run
- Screenshot of Docker Hub showing the pushed image
- Screenshots of the calculation page adding, listing, reading, editing, and deleting calculations
- Reflection document
