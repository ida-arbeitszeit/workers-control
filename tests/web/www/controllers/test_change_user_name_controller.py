from tests.web.base_test_case import BaseTestCase
from tests.web.www.forms import ChangeUserNameFormImpl as Form
from workers_control.web.www.controllers.change_user_name_controller import (
    ChangeUserNameController,
)


class ChangeUserNameControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(ChangeUserNameController)

    def test_for_member_request_carries_user_id_new_name_and_password(self) -> None:
        member = self.member_generator.create_member()
        self.session.login_member(member=member)
        form = Form.from_values(new_name="New Name", current_password="pw1")
        request = self.controller.process_change_user_name_request(form)
        assert request.user_id == member
        assert request.new_name == "New Name"
        assert request.current_password == "pw1"

    def test_for_company_request_carries_company_id(self) -> None:
        company = self.company_generator.create_company()
        self.session.login_company(company=company)
        form = Form.from_values(new_name="X Inc", current_password="pw2")
        request = self.controller.process_change_user_name_request(form)
        assert request.user_id == company

    def test_for_accountant_request_carries_accountant_id(self) -> None:
        accountant = self.accountant_generator.create_accountant()
        self.session.login_accountant(accountant=accountant)
        form = Form.from_values(new_name="A", current_password="pw3")
        request = self.controller.process_change_user_name_request(form)
        assert request.user_id == accountant

    def test_that_surrounding_whitespace_is_stripped_from_new_name(self) -> None:
        member = self.member_generator.create_member()
        self.session.login_member(member=member)
        form = Form.from_values(new_name="   Padded Name   ", current_password="pw")
        request = self.controller.process_change_user_name_request(form)
        assert request.new_name == "Padded Name"

    def test_that_whitespace_only_name_becomes_empty_string(self) -> None:
        member = self.member_generator.create_member()
        self.session.login_member(member=member)
        form = Form.from_values(new_name="   \t  ", current_password="pw")
        request = self.controller.process_change_user_name_request(form)
        assert request.new_name == ""
