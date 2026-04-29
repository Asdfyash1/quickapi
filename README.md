# QuickAPI

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)

**A CLI tool to scaffold production-ready FastAPI projects in seconds.**

Stop writing boilerplate. QuickAPI generates a complete, well-structured FastAPI project with routes, models, database, Docker, tests, and more — ready to run immediately.

## Features

- **Instant Setup** — Generate a full FastAPI project with one command
- **CRUD Routes** — Auto-generated REST API with list, create, get, delete endpoints
- **SQLite Database** — Pre-configured database with init and connection management
- **Authentication** — Optional token-based auth with login endpoint
- **Docker Ready** — Dockerfile + docker-compose.yml included by default
- **CORS Middleware** — Pre-configured cross-origin support
- **Test Suite** — Pytest tests generated for all endpoints
- **Clean Architecture** — Organized package structure following best practices
- **Customizable** — Choose features, port, Python version via CLI flags

## Installation

```bash
git clone https://github.com/Asdfyash1/quickapi.git
cd quickapi
pip install -e .
```

## Quick Start

Create a new project:

```bash
quickapi new myapp
```

This generates:

```
myapp/
├── myapp/
│   ├── __init__.py
│   ├── main.py          # FastAPI app & middleware
│   ├── routes.py         # CRUD API routes
│   ├── models.py         # Pydantic schemas
│   ├── database.py       # SQLite setup
│   └── config.py         # App configuration
├── tests/
│   └── test_api.py       # Endpoint tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

Run it:

```bash
cd myapp
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn myapp.main:app --reload
```

API docs at: http://localhost:8000/docs

## Usage

### Create with all features

```bash
quickapi new myapp --auth --database sqlite --port 3000
```

### Create a minimal API (no database, no Docker)

```bash
quickapi new myapp --database none --no-docker
```

### List available features

```bash
quickapi templates
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--description, -d` | Project description | "A FastAPI application" |
| `--database, -db` | Database backend (`sqlite` or `none`) | `sqlite` |
| `--auth` | Include token authentication | off |
| `--no-docker` | Skip Docker files | included |
| `--no-tests` | Skip test files | included |
| `--no-cors` | Disable CORS middleware | enabled |
| `--port, -p` | Default port number | 8000 |
| `--python` | Python version for Dockerfile | 3.12 |
| `--output, -o` | Output directory | current dir |

## Generated API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Welcome message |
| `GET` | `/health` | Health check |
| `GET` | `/api/items` | List all items |
| `POST` | `/api/items` | Create an item |
| `GET` | `/api/items/{id}` | Get item by ID |
| `DELETE` | `/api/items/{id}` | Delete an item |
| `POST` | `/auth/login` | Login (with `--auth`) |

## Development

```bash
git clone https://github.com/Asdfyash1/quickapi.git
cd quickapi
python -m venv .venv
source .venv/bin/activate
pip install -e .
pytest tests/ -v
```

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

**Yashwanth** — [GitHub](https://github.com/Asdfyash1)
