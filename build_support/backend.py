from typing import Any, Dict, Optional

from setuptools import build_meta as _orig
from setuptools.build_meta import *  # noqa: F403,F401

from build_support import translations


def build_wheel(  # type: ignore[no-redef]
    wheel_directory: str,
    config_settings: Optional[Dict[str, Any]] = None,
    metadata_directory: Optional[str] = None,
) -> str:
    translations.compile_messages()
    return _orig.build_wheel(wheel_directory, config_settings, metadata_directory)
