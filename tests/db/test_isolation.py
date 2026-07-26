from sqlalchemy import create_engine, text

from tests.db.base_test_case import DatabaseTestCase
from tests.db.dependency_injection import provide_test_database_uri


class RollbackIsolationTests(DatabaseTestCase):
    """Assert that DatabaseTestCase really undoes what a test wrote.

    The two tests below create the same member, so whichever of them runs
    second fails if the data of the other one survived.  That way the
    assertion does not depend on the order in which they run.
    """

    EMAIL = "isolation@test.example"

    def test_that_a_member_of_another_test_is_not_visible_1(self) -> None:
        self._create_member_that_must_not_exist_yet()

    def test_that_a_member_of_another_test_is_not_visible_2(self) -> None:
        self._create_member_that_must_not_exist_yet()

    def test_that_a_commit_does_not_reach_the_database(self) -> None:
        self.member_generator.create_member(email=self.EMAIL)
        self.test_session.commit()
        assert self._members_in_database() == 0

    def _create_member_that_must_not_exist_yet(self) -> None:
        assert not self.database_gateway.get_members().with_email_address(self.EMAIL)
        self.member_generator.create_member(email=self.EMAIL)

    def _members_in_database(self) -> int:
        """Count the members that are visible outside of the transaction of
        this test.
        """
        engine = create_engine(provide_test_database_uri())
        try:
            with engine.connect() as connection:
                count = connection.execute(text("select count(*) from member")).scalar()
        finally:
            engine.dispose()
        assert count is not None
        return count
