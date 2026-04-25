from unittest import TestCase
from uuid import uuid4

from tests.data_generators import CompanyGenerator, MemberGenerator
from tests.interactors.dependency_injection import get_dependency_injector
from workers_control.core.interactors.get_company_dashboard import (
    GetCompanyDashboardInteractor,
)


class GeneralInteractorTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.interactor = self.injector.get(GetCompanyDashboardInteractor)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.member_generator = self.injector.get(MemberGenerator)

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

    def test_that_dashboard_shows_company_email(self) -> None:
        expected_mail = "t@tmail.com"
        company = self.company_generator.create_company_record(email=expected_mail)
        response = self.interactor.get_dashboard(company.id)
        self.assertEqual(response.company_info.email, expected_mail)

    def test_that_dashboard_shows_that_company_has_no_workers(self) -> None:
        company = self.company_generator.create_company_record(workers=None)
        response = self.interactor.get_dashboard(company.id)
        self.assertFalse(response.has_workers)

    def test_that_dashboard_shows_that_company_has_workers(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        response = self.interactor.get_dashboard(company.id)
        self.assertTrue(response.has_workers)
