import importlib

from flask import Flask, current_app

from .interface import EmailPlugin


def load_email_plugin(app: Flask) -> None:
    config = app.config["MAIL_PLUGIN"]
    module_name, class_name = config.split(":", maxsplit=1)
    module = importlib.import_module(module_name)
    plugin_class = getattr(module, class_name)
    assert issubclass(plugin_class, EmailPlugin)
    plugin = plugin_class()
    app.extensions["woco_email_plugin"] = plugin


def get_mail_service() -> EmailPlugin:
    return current_app.extensions["woco_email_plugin"]
