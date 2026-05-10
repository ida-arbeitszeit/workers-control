import importlib

from flask import current_app

from workers_control.core.injector import Injector
from workers_control.email_sending_worker.interface import EmailSenderPlugin


def provide_email_sender(injector: Injector) -> EmailSenderPlugin:
    config = current_app.config["MAIL_SENDER_PLUGIN"]
    module_name, class_name = config.split(":", maxsplit=1)
    module = importlib.import_module(module_name)
    plugin_class = getattr(module, class_name)
    assert issubclass(plugin_class, EmailSenderPlugin)
    return injector.get(plugin_class)
