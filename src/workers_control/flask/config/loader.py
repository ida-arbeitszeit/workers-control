import os
from typing import Any

from flask import Flask


def load_configuration(app: Flask, dev_or_test_config: Any = None) -> None:
    """Load the right configuration for the application.

    If a test or dev configuration is provided, we load it.

    Else, we first set default values from
    `workers_control.flask.config.production_defaults`.
    Then, on top of this, we load the first (production) configuration we can
    find from the following sources:
    - From path WOCO_CONFIGURATION_PATH
    - From path /etc/workers-control/workers-control.py
    """
    if dev_or_test_config:
        app.config.from_object(dev_or_test_config)
    else:
        app.config.from_object("workers_control.flask.config.production_defaults")
        if config_path := os.environ.get("WOCO_CONFIGURATION_PATH"):
            app.config.from_pyfile(config_path)
        else:
            app.config.from_pyfile(
                "/etc/workers-control/workers-control.py", silent=True
            )
