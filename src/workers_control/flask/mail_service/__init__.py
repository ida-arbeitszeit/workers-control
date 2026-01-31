import importlib

from flask import current_app

from workers_control.core.injector import Injector

from .interface import EmailPlugin


def provide_email_service(injector: Injector) -> EmailPlugin:
    if plugin := current_app.extensions.get("woco_email_plugin"):
        return plugin
    plugin = _create_email_plugin_from_config(injector)
    _store_email_plugin(plugin)
    return plugin


def _create_email_plugin_from_config(injector: Injector) -> EmailPlugin:
    config = current_app.config["MAIL_PLUGIN"]
    module_name, class_name = config.split(":", maxsplit=1)
    module = importlib.import_module(module_name)
    plugin_class = getattr(module, class_name)
    assert issubclass(plugin_class, EmailPlugin)
    plugin = injector.get(plugin_class)
    return plugin


def _store_email_plugin(plugin: EmailPlugin) -> None:
    current_app.extensions["woco_email_plugin"] = plugin
