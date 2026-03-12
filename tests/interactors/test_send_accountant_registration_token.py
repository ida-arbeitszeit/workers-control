from workers_control.core import email_notifications
from workers_control.core.interactors.send_accountant_registration_token import (
    SendAccountantRegistrationTokenInteractor,
)

from .base_test_case import BaseTestCase


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(SendAccountantRegistrationTokenInteractor)

    def test_can_send_registration_token_to_email_that_is_already_registered_as_member(
        self,
    ) -> None:
        member_email = "test@test.test"
        self.member_generator.create_member(email=member_email)
        response = self.send_invitation(member_email)
        assert response.has_been_sent
        self.delivered_notifications()

    def test_can_send_registration_token_to_email_that_is_already_registered_as_company(
        self,
    ) -> None:
        company_email = "test@test.test"
        self.company_generator.create_company_record(email=company_email)
        response = self.send_invitation(company_email)

        assert response.has_been_sent
        self.delivered_notifications()

    def test_cannot_send_registration_token_to_email_that_is_already_registered_as_accountant(
        self,
    ) -> None:
        accountant_email = "test@test.test"
        self.accountant_generator.create_accountant(email_address=accountant_email)
        pre_interactor_invitation_count = len(self.delivered_notifications())
        response = self.send_invitation(accountant_email)
        assert not response.has_been_sent
        assert len(self.delivered_notifications()) == pre_interactor_invitation_count

    def test_that_invitation_is_presented_for_correct_email_address(self) -> None:
        expected_email = "test@mail.test"
        response = self.send_invitation(expected_email)
        assert response.has_been_sent
        self.assertEqual(
            self.latest_delivered_notification().email_address, expected_email
        )

    def test_can_send_registration_token_twice_to_same_email_that_has_not_registered(
        self,
    ) -> None:
        email = "test@test.test"
        response = self.send_invitation(email)
        assert response.has_been_sent
        initial_count = len(self.delivered_notifications())
        response = self.send_invitation(email)
        assert response.has_been_sent
        assert len(self.delivered_notifications()) == initial_count + 1

    def send_invitation(
        self, email: str
    ) -> SendAccountantRegistrationTokenInteractor.Response:
        return self.interactor.send_accountant_registration_token(
            request=SendAccountantRegistrationTokenInteractor.Request(email=email)
        )

    def latest_delivered_notification(self) -> email_notifications.AccountantInvitation:
        notifications = self.delivered_notifications()
        assert notifications
        return notifications[-1]

    def delivered_notifications(self) -> list[email_notifications.AccountantInvitation]:
        return [
            m
            for m in self.email_sender.get_messages_sent()
            if isinstance(m, email_notifications.AccountantInvitation)
        ]
