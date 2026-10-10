from functools import cache

from build_support.translations import compile_messages


@cache
def compile_translation_catalogs() -> None:
    # The .mo files are build artifacts that an editable install does not
    # produce, so tests that expect translated output compile them first.
    compile_messages()
