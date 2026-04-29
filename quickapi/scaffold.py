"""Project scaffolding engine."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from jinja2 import Environment, BaseLoader


@dataclass
class ProjectConfig:
    name: str
    description: str = "A FastAPI application"
    template: str = "basic"
    database: str = "sqlite"
    include_docker: bool = True
    include_auth: bool = False
    include_cors: bool = True
    include_tests: bool = True
    python_version: str = "3.12"
    port: int = 8000


TEMPLATES: dict[str, dict[str, str]] = {}

# ── main.py ──────────────────────────────────────────────────
TEMPLATES["main.py"] = '''\
"""{{ config.description }}"""

from contextlib import asynccontextmanager
{% if config.database != "none" %}
from {{ config.name }}.database import init_db
{% endif %}
from fastapi import FastAPI
{% if config.include_cors %}
from fastapi.middleware.cors import CORSMiddleware
{% endif %}
from {{ config.name }}.routes import router
{% if config.include_auth %}
from {{ config.name }}.auth import auth_router
{% endif %}


{% if config.database != "none" %}
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
{% endif %}


app = FastAPI(
    title="{{ config.name }}",
    description="{{ config.description }}",
    version="0.1.0",
{% if config.database != "none" %}
    lifespan=lifespan,
{% endif %}
)

{% if config.include_cors %}
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
{% endif %}

app.include_router(router, prefix="/api")
{% if config.include_auth %}
app.include_router(auth_router, prefix="/auth", tags=["auth"])
{% endif %}


@app.get("/")
async def root():
    return {"message": "Welcome to {{ config.name }}!", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
'''

# ── routes.py ────────────────────────────────────────────────
TEMPLATES["routes.py"] = '''\
"""API routes."""

from fastapi import APIRouter, HTTPException
{% if config.database != "none" %}
from {{ config.name }}.models import Item, ItemCreate, ItemResponse
from {{ config.name }}.database import get_db
{% endif %}

router = APIRouter()

{% if config.database != "none" %}

@router.get("/items", response_model=list[ItemResponse])
async def list_items():
    """List all items."""
    db = get_db()
    cursor = db.execute("SELECT id, name, description, created_at FROM items ORDER BY created_at DESC")
    rows = cursor.fetchall()
    return [ItemResponse(id=r[0], name=r[1], description=r[2], created_at=r[3]) for r in rows]


@router.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate):
    """Create a new item."""
    db = get_db()
    cursor = db.execute(
        "INSERT INTO items (name, description) VALUES (?, ?)",
        (item.name, item.description),
    )
    db.commit()
    return ItemResponse(
        id=cursor.lastrowid,
        name=item.name,
        description=item.description,
    )


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    """Get an item by ID."""
    db = get_db()
    cursor = db.execute("SELECT id, name, description, created_at FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse(id=row[0], name=row[1], description=row[2], created_at=row[3])


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    """Delete an item."""
    db = get_db()
    cursor = db.execute("DELETE FROM items WHERE id = ?", (item_id,))
    db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")

{% else %}

@router.get("/items")
async def list_items():
    """List items (in-memory demo)."""
    return [{"id": 1, "name": "Example Item", "description": "A sample item"}]

{% endif %}
'''

# ── models.py ────────────────────────────────────────────────
TEMPLATES["models.py"] = '''\
"""Pydantic models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[str] = None
'''

# ── database.py ──────────────────────────────────────────────
TEMPLATES["database.py"] = '''\
"""Database setup and connection."""

import sqlite3
from pathlib import Path

DB_PATH = Path("data/app.db")
_connection: sqlite3.Connection | None = None


def init_db() -> None:
    """Initialize the database and create tables."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()


def get_db() -> sqlite3.Connection:
    """Get database connection (singleton)."""
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        _connection.row_factory = sqlite3.Row
    return _connection
'''

# ── auth.py ──────────────────────────────────────────────────
TEMPLATES["auth.py"] = '''\
"""Simple token-based authentication."""

from datetime import datetime, timedelta
import hashlib
import secrets

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

auth_router = APIRouter()
security = HTTPBearer()

_tokens: dict[str, dict] = {}


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


@auth_router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Generate an access token."""
    token = secrets.token_urlsafe(32)
    _tokens[token] = {
        "username": request.username,
        "created_at": datetime.utcnow().isoformat(),
    }
    return TokenResponse(access_token=token)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Validate token and return user info."""
    token = credentials.credentials
    user = _tokens.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
'''

# ── config.py ────────────────────────────────────────────────
TEMPLATES["config.py"] = '''\
"""Application configuration."""

import os


class Settings:
    APP_NAME: str = "{{ config.name }}"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/app.db")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "{{ config.port }}"))


settings = Settings()
'''

# ── Dockerfile ───────────────────────────────────────────────
TEMPLATES["Dockerfile"] = '''\
FROM python:{{ config.python_version }}-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {{ config.port }}

CMD ["uvicorn", "{{ config.name }}.main:app", "--host", "0.0.0.0", "--port", "{{ config.port }}"]
'''

# ── docker-compose.yml ───────────────────────────────────────
TEMPLATES["docker-compose.yml"] = '''\
services:
  api:
    build: .
    ports:
      - "{{ config.port }}:{{ config.port }}"
    environment:
      - DEBUG=true
    volumes:
      - ./data:/app/data
    restart: unless-stopped
'''

# ── requirements.txt ─────────────────────────────────────────
TEMPLATES["requirements.txt"] = '''\
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.0
{% if config.database != "none" %}
# SQLite is built-in; add drivers here for PostgreSQL/MySQL
{% endif %}
'''

# ── test_api.py ──────────────────────────────────────────────
TEMPLATES["test_api.py"] = '''\
"""API tests."""

from fastapi.testclient import TestClient
from {{ config.name }}.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


{% if config.database != "none" %}
def test_create_and_get_item():
    response = client.post("/api/items", json={"name": "Test", "description": "A test item"})
    assert response.status_code == 201
    item_id = response.json()["id"]

    response = client.get(f"/api/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test"


def test_list_items():
    response = client.get("/api/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delete_item():
    response = client.post("/api/items", json={"name": "ToDelete"})
    item_id = response.json()["id"]

    response = client.delete(f"/api/items/{item_id}")
    assert response.status_code == 204


def test_item_not_found():
    response = client.get("/api/items/99999")
    assert response.status_code == 404
{% else %}
def test_list_items():
    response = client.get("/api/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
{% endif %}
'''

# ── .env.example ─────────────────────────────────────────────
TEMPLATES[".env.example"] = '''\
DEBUG=true
HOST=0.0.0.0
PORT={{ config.port }}
'''

# ── project .gitignore ───────────────────────────────────────
TEMPLATES["project_gitignore"] = '''\
__pycache__/
*.py[cod]
*.so
.Python
build/
dist/
*.egg-info/
.env
.venv
venv/
data/
*.db
*.sqlite3
.pytest_cache/
.coverage
htmlcov/
.idea/
.vscode/
*.swp
.DS_Store
'''

# ── project README ───────────────────────────────────────────
TEMPLATES["project_readme"] = '''\
# {{ config.name }}

{{ config.description }}

## Quick Start

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn {{ config.name }}.main:app --reload --port {{ config.port }}
```

API docs available at: http://localhost:{{ config.port }}/docs

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | Health check |
| GET | `/api/items` | List all items |
| POST | `/api/items` | Create an item |
| GET | `/api/items/{id}` | Get item by ID |
| DELETE | `/api/items/{id}` | Delete an item |
{% if config.include_auth %}
| POST | `/auth/login` | Get access token |
{% endif %}

{% if config.include_docker %}
## Docker

```bash
docker compose up --build
```
{% endif %}

## Testing

```bash
pip install pytest httpx
pytest tests/ -v
```

## Project Structure

```
{{ config.name }}/
├── {{ config.name }}/
│   ├── __init__.py
│   ├── main.py          # FastAPI app & middleware
│   ├── routes.py         # API route handlers
│   ├── models.py         # Pydantic schemas
{% if config.database != "none" %}
│   ├── database.py       # Database setup
{% endif %}
{% if config.include_auth %}
│   ├── auth.py           # Authentication
{% endif %}
│   └── config.py         # App configuration
├── tests/
│   └── test_api.py
{% if config.include_docker %}
├── Dockerfile
├── docker-compose.yml
{% endif %}
├── requirements.txt
├── .env.example
└── README.md
```
'''


def _render(template_str: str, config: ProjectConfig) -> str:
    env = Environment(loader=BaseLoader(), keep_trailing_newline=True)
    template = env.from_string(template_str)
    return template.render(config=config)


def scaffold_project(config: ProjectConfig, output_dir: Path) -> list[str]:
    """Generate a FastAPI project from templates."""
    project_root = output_dir / config.name
    pkg_dir = project_root / config.name
    tests_dir = project_root / "tests"
    created_files: list[str] = []

    pkg_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)

    # Package __init__.py
    init_content = f'"""{config.description}"""\n\n__version__ = "0.1.0"\n'
    _write(pkg_dir / "__init__.py", init_content, created_files)

    # Core files
    _write(pkg_dir / "main.py", _render(TEMPLATES["main.py"], config), created_files)
    _write(pkg_dir / "routes.py", _render(TEMPLATES["routes.py"], config), created_files)
    _write(pkg_dir / "models.py", _render(TEMPLATES["models.py"], config), created_files)
    _write(pkg_dir / "config.py", _render(TEMPLATES["config.py"], config), created_files)

    if config.database != "none":
        _write(pkg_dir / "database.py", _render(TEMPLATES["database.py"], config), created_files)

    if config.include_auth:
        _write(pkg_dir / "auth.py", _render(TEMPLATES["auth.py"], config), created_files)

    # Tests
    _write(tests_dir / "__init__.py", "", created_files)
    _write(tests_dir / "test_api.py", _render(TEMPLATES["test_api.py"], config), created_files)

    # Root files
    _write(project_root / "requirements.txt", _render(TEMPLATES["requirements.txt"], config), created_files)
    _write(project_root / ".env.example", _render(TEMPLATES[".env.example"], config), created_files)
    _write(project_root / ".gitignore", _render(TEMPLATES["project_gitignore"], config), created_files)
    _write(project_root / "README.md", _render(TEMPLATES["project_readme"], config), created_files)

    if config.include_docker:
        _write(project_root / "Dockerfile", _render(TEMPLATES["Dockerfile"], config), created_files)
        _write(project_root / "docker-compose.yml", _render(TEMPLATES["docker-compose.yml"], config), created_files)

    return created_files


def _write(path: Path, content: str, created: list[str]) -> None:
    path.write_text(content)
    created.append(str(path))
