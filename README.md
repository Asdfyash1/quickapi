# QuickAPI

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-blueviolet.svg)](#ai-powered-features)

**A CLI tool to scaffold production-ready FastAPI projects in seconds — with AI-powered route generation from natural language.**

Stop writing boilerplate. QuickAPI generates a complete, well-structured FastAPI project with routes, models, database, Docker, tests, and more — ready to run immediately. With AI mode, describe your API in plain English and get production-ready code generated instantly.

## Features

- **Instant Setup** — Generate a full FastAPI project with one command
- **CRUD Routes** — Auto-generated REST API with list, create, get, delete endpoints
- **SQLite Database** — Pre-configured database with init and connection management
- **Authentication** — Optional token-based auth with login endpoint
- **Docker Ready** — Dockerfile + docker-compose.yml included by default
- **CORS Middleware** — Pre-configured cross-origin support
- **Test Suite** — Pytest tests generated for all endpoints
- **Clean Architecture** — Organized package structure following best practices

### AI-Powered Features

- **AI Generate** — Describe an API in natural language, get complete FastAPI routes and models
- **AI Add Endpoint** — Add new endpoints to existing projects with plain English descriptions
- **Multi-Provider** — Works with OpenAI, Google Gemini, and NVIDIA APIs

## Installation

```bash
git clone https://github.com/Asdfyash1/quickapi.git
cd quickapi
pip install -e .
```

## Quick Start

### Scaffold a project

```bash
quickapi new myapp
```

### Scaffold with all features

```bash
quickapi new myapp --auth --database sqlite --port 3000
```

### AI: Generate API from description

```bash
export OPENAI_API_KEY="your-key"   # or GEMINI_API_KEY or NVIDIA_API_KEY

quickapi generate "a blog API with posts, comments, and tags"
quickapi generate "user management with registration, login, profiles" -o ./output
```

### AI: Add endpoint to existing project

```bash
quickapi add-endpoint "search items by name with pagination" -r myapp/routes.py
```

## AI Setup

Set one of these environment variables to enable AI features:

| Provider | Environment Variable | Default Model |
|----------|---------------------|---------------|
| OpenAI | `OPENAI_API_KEY` | `gpt-4o-mini` |
| Google Gemini | `GEMINI_API_KEY` | `gemini-2.0-flash` |
| NVIDIA | `NVIDIA_API_KEY` | `meta/llama-3.1-8b-instruct` |

Override the model with: `OPENAI_MODEL`, `GEMINI_MODEL`, or `NVIDIA_MODEL`.

## Commands

| Command | Description |
|---------|-------------|
| `new NAME` | Scaffold a new FastAPI project |
| `templates` | List available features and flags |
| `generate DESC` | AI: Generate API from natural language |
| `add-endpoint DESC` | AI: Generate endpoint for existing routes |

### `new` Options

| Flag | Description | Default |
|------|-------------|---------|
| `--description, -d` | Project description | "A FastAPI application" |
| `--database, -db` | Database (`sqlite` or `none`) | `sqlite` |
| `--auth` | Include authentication | off |
| `--no-docker` | Skip Docker files | included |
| `--no-tests` | Skip test files | included |
| `--no-cors` | Disable CORS | enabled |
| `--port, -p` | Port number | 8000 |
| `--python` | Python version | 3.12 |
| `--output, -o` | Output directory | current dir |

## Generated Project Structure

```
myapp/
├── myapp/
│   ├── __init__.py
│   ├── main.py          # FastAPI app & middleware
│   ├── routes.py         # CRUD API routes
│   ├── models.py         # Pydantic schemas
│   ├── database.py       # SQLite setup
│   ├── auth.py           # Authentication (with --auth)
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
