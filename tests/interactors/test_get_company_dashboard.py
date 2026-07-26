from uuid import uuid4

from tests.base_test_case import BaseTestCase
from workers_control.core.interactors.get_company_dashboard import (
    GetCompanyDashboardInteractor,
)


class GeneralInteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(GetCompanyDashboardInteractor)

    def test_that_retrieving_dashboard_for_nonexisting_company_fails(self) -> None:
        with self.assertRaises(GetCompanyDashboardInteractor.Failure):
            self.interactor.get_dashboard(uuid4())

    def test_that_retrieving_dashboard_for_existing_company_succeeds(self) -> None:
        company = self.company_generator.create_company_record()
        response = self.interactor.get_dashboard(company.id)
        self.assertIsInstance(response, GetCompanyDashboardInteractor.Response)

    def test_that_dashboard_shows_company_name(self) -> None:
        expected_name = "test coop name"
        company = self.company_generator.create_company_record(name=expected_name)
        response = self.interactor.get_dashboard(company.id)
        self.assertEqual(response.company_info.name, expected_name)

    def test_that_dashboard_shows_company_id(self) -> None:
        company = self.company_generator.create_company_record()
        response = self.interactor.get_dashboard(company.id)
        self.assertEqual(response.company_info.id, company.id)
