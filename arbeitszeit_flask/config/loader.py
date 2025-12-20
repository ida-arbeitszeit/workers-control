import os
from typing import Any

from flask import Flask


def load_configuration(app: Flask, dev_or_test_config: Any = None) -> None:
    """Load the right configuration for the application.

    If a test or dev configuration is provided, we load it.

    Else, we first set default values from
    `arbeitszeit_flask.config.production_defaults`.
    Then, on top of this, we load the first (production) configuration we can
    find from the following sources:
    - From path ARBEITSZEITAPP_CONFIGURATION_PATH
    - From path /etc/arbeitszeitapp/arbeitszeitapp.py
    """
    if dev_or_test_config:
        app.config.from_object(dev_or_test_config)
    else:
        app.config.from_object("arbeitszeit_flask.config.production_defaults")
        if config_path := os.environ.get("ARBEITSZEITAPP_CONFIGURATION_PATH"):
            app.config.from_pyfile(config_path)
        else:
            app.config.from_pyfile("/etc/arbeitszeitapp/arbeitszeitapp.py", silent=True)
