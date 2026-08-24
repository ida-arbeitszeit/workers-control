from typing import Optional
from uuid import uuid4

from parameterized import parameterized

from tests.data_generators import CollaborationGenerator
from tests.flask_integration.base_test_case import LogInUser

from .base_test_case import ViewTestCase


class UserAccessTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.collab_generator = self.injector.get(CollaborationGenerator)

    @parameterized.expand(
        [
            (LogInUser.accountant, 404),
            (LogInUser.company, 404),
            (LogInUser.member, 404),
        ]
    )
    def test_get_404_for_logged_in_users_when_collab_does_not_exist(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        url = f"/user/collaboration_summary/{uuid4()}"
        self.assert_response_has_expected_code(
            url=url,
            method="get",
            login=login,
            expected_code=expected_code,
        )

    def test_get_302_for_unauthenticated_users_when_collab_does_not_exist(self) -> None:
        url = f"/user/collaboration_summary/{uuid4()}"
        self.assert_response_has_expected_code(
            url=url,
            method="get",
            login=None,
            expected_code=302,
        )

    @parameterized.expand(
        [
            (LogInUser.accountant, 200),
            (LogInUser.company, 200),
            (LogInUser.member, 200),
        ]
    )
    def test_get_200_for_logged_in_users_when_collab_does_exist(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        collab = self.collab_generator.create_collaboration()
        url = f"/user/collaboration_summary/{collab}"
        self.assert_response_has_expected_code(
            url=url,
            method="get",
            login=login,
            expected_code=expected_code,
        )

    def test_get_302_for_unauthenticated_users_when_collab_does_exist(self) -> None:
        collab = self.collab_generator.create_collaboration()
        url = f"/user/collaboration_summary/{collab}"
        self.assert_response_has_expected_code(
            url=url,
            method="get",
            login=None,
            expected_code=302,
        )
