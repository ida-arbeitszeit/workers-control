from uuid import UUID, uuid4

from workers_control.core import email_notifications
from workers_control.core.interactors import change_user_name as interactor
from workers_control.core.interactors.get_user_account_details import (
    GetUserAccountDetailsInteractor,
)
from workers_control.core.interactors.get_user_account_details import (
    Request as GetUserAccountDetailsRequest,
)

from ..base_test_case import BaseTestCase


def create_request(
    user_id: UUID, new_name: str, current_password: str
) -> interactor.Request:
    return interactor.Request(
        user_id=user_id,
        new_name=new_name,
        current_password=current_password,
    )


class ChangeUserNameTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(interactor.ChangeUserNameInteractor)
        self.get_account_details = self.injector.get(GetUserAccountDetailsInteractor)

    def get_name(self, user_id: UUID) -> str:
        response = self.get_account_details.get_user_account_details(
            GetUserAccountDetailsRequest(user_id=user_id)
        )
        assert response.user_info
        return response.user_info.name

    def test_that_request_is_rejected_for_unknown_user_id(self) -> None:
        response = self.interactor.change_user_name(
            create_request(
                user_id=uuid4(), new_name="New Name", current_password="some_pw"
            )
        )
        assert response.rejection_reason == response.RejectionReason.user_not_found

    def test_that_member_can_change_name(self) -> None:
        password = "secret_pw"
        member_id = self.member_generator.create_member(password=password)
        response = self.interactor.change_user_name(
            create_request(
                user_id=member_id, new_name="New Name", current_password=password
            )
        )
        assert response.rejection_reason is None
        assert self.get_name(member_id) == "New Name"

    def test_that_company_can_change_name(self) -> None:
        password = "secret_pw"
        company_id = self.company_generator.create_company(password=password)
        response = self.interactor.change_user_name(
            create_request(
                user_id=company_id, new_name="New Company", current_password=password
            )
        )
        assert response.rejection_reason is None
        assert self.get_name(company_id) == "New Company"

    def test_that_accountant_can_change_name(self) -> None:
        password = "secret_pw"
        accountant_id = self.accountant_generator.create_accountant(password=password)
        response = self.interactor.change_user_name(
            create_request(
                user_id=accountant_id,
                new_name="New Accountant",
                current_password=password,
            )
        )
        assert response.rejection_reason is None
        assert self.get_name(accountant_id) == "New Accountant"

    def test_that_request_is_rejected_with_wrong_password(self) -> None:
        password = "correct_pw"
        member_id = self.member_generator.create_member(password=password)
        response = self.interactor.change_user_name(
            create_request(
                user_id=member_id,
                new_name="New Name",
                current_password=password + "wrong",
            )
        )
        assert response.rejection_reason == response.RejectionReason.incorrect_password

    def test_that_empty_name_is_rejected(self) -> None:
        password = "secret_pw"
        member_id = self.member_generator.create_member(password=password)
        response = self.interactor.change_user_name(
            create_request(user_id=member_id, new_name="", current_password=password)
        )
        assert response.rejection_reason == response.RejectionReason.invalid_name

    def test_that_overly_long_name_is_rejected(self) -> None:
        password = "secret_pw"
        member_id = self.member_generator.create_member(password=password)
        response = self.interactor.change_user_name(
            create_request(
                user_id=member_id,
                new_name="a" * (interactor.MAX_NAME_LENGTH + 1),
                current_password=password,
            )
        )
        assert response.rejection_reason == response.RejectionReason.invalid_name


class ChangeUserNameNotificationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(interactor.ChangeUserNameInteractor)

    def test_that_confirmation_email_is_sent_on_success(self) -> None:
        password = "secret_pw"
        member_id = self.member_generator.create_member(
            email="test@test.test", password=password
        )
        self.interactor.change_user_name(
            create_request(
                user_id=member_id, new_name="New Name", current_password=password
            )
        )
        confirmations = self._delivered_confirmations()
        assert len(confirmations) == 1
        assert confirmations[0].email_address == "test@test.test"
        assert confirmations[0].new_name == "New Name"

    def test_that_no_email_is_sent_on_wrong_password(self) -> None:
        password = "secret_pw"
        member_id = self.member_generator.create_member(password=password)
        self.interactor.change_user_name(
            create_request(
                user_id=member_id,
                new_name="New Name",
                current_password=password + "x",
            )
        )
        assert not self._delivered_confirmations()

    def test_that_no_email_is_sent_on_invalid_name(self) -> None:
        password = "secret_pw"
        member_id = self.member_generator.create_member(password=password)
        self.interactor.change_user_name(
            create_request(user_id=member_id, new_name="", current_password=password)
        )
        assert not self._delivered_confirmations()

    def _delivered_confirmations(
        self,
    ) -> list[email_notifications.NameChangeConfirmation]:
        return [
            m
            for m in self.email_sender.get_messages_sent()
            if isinstance(m, email_notifications.NameChangeConfirmation)
        ]
