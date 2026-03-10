from pathlib import Path

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from flask import Config as FlaskConfig

from workers_control.db.db import Database


def _get_alembic_config(flask_config: FlaskConfig) -> AlembicConfig:
    alembic_config = Path(flask_config["ALEMBIC_CONFIG"])
    if not alembic_config.is_file():
        raise FileNotFoundError(f"Alembic config file not found: {alembic_config}")
    return AlembicConfig(alembic_config)


def _upgrade_to_head(alembic_config: AlembicConfig) -> None:
    alembic_command.upgrade(alembic_config, "head")


def _upgrade_to_head_if_database_is_fresh(alembic_config: AlembicConfig) -> None:
    """
    The following command's only purpose is to trigger an upgrade
    if database is fresh.
    See customized migration logic in alembic's `env.py`.
    """
    alembic_command.current(alembic_config)


def run_db_migrations(flask_config: FlaskConfig, db: Database) -> None:
    alembic_config = _get_alembic_config(flask_config)
    with db.engine.begin() as connection:
        alembic_config.attributes["connection"] = connection
        if flask_config["AUTO_MIGRATE"]:
            _upgrade_to_head(alembic_config)
        else:
            _upgrade_to_head_if_database_is_fresh(alembic_config)
