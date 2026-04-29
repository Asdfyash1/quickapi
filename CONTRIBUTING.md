# Contributing to QuickAPI

Thanks for your interest in contributing! Here's how to get started.

## Setup

```bash
git clone https://github.com/Asdfyash1/quickapi.git
cd quickapi
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install pytest
```

## Running Tests

```bash
pytest tests/ -v
```

## How to Contribute

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests to make sure everything passes
5. Commit: `git commit -m "Add my feature"`
6. Push: `git push origin feature/my-feature`
7. Open a Pull Request

## Ideas for Contributions

- Add PostgreSQL/MySQL database templates
- Add WebSocket endpoint templates
- Add background task (Celery/ARQ) scaffolding
- Add OAuth2/JWT authentication templates
- Add GraphQL support
- Add Alembic migration scaffolding
- Add more AI provider integrations
- Add interactive mode (prompt-based project creation)
- Add deployment configs (Railway, Fly.io, Render)

## Code Style

- Follow PEP 8
- Use type hints
- Keep functions focused and small
- Add docstrings to public functions

## Reporting Bugs

Open an issue with:
- What you expected to happen
- What actually happened
- Steps to reproduce
- Python version and OS
