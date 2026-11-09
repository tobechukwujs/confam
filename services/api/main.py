"""Entry point: `uv run fastapi dev services/api/main.py`."""

from confam_api.app import create_app

app = create_app()
