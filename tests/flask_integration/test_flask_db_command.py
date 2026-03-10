from workers_control.flask.commands import run_alembic

from .base_test_case import FlaskTestCase


class FlaskDbTests(FlaskTestCase):
    def test_can_query_migration_history_without_crashing(self) -> None:
        run_alembic(
            tuple(
                "history",
            )
        )
