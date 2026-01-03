import json
from logging.config import dictConfig
from pathlib import Path

from workers_control.flask import create_app

config_path = Path(__file__).parent / "logging_config.json"

with open(config_path, "r") as f:
    config = json.load(f)
    dictConfig(config)

app = create_app()

if __name__ == "__main__":
    app.run()
