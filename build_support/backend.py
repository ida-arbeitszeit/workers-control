from setuptools import build_meta as _orig
from setuptools.build_meta import *  # noqa: F403,F401

from build_support import translations


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):  # type: ignore[no-redef]
    translations.compile_messages()
    return _orig.build_wheel(wheel_directory, config_settings, metadata_directory)
