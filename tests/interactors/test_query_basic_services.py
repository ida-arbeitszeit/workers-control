from datetime import timedelta

from tests.datetime_service import datetime_utc
from tests.interactors.base_test_case import BaseTestCase
from workers_control.core.interactors.query_basic_services import (
    QueryBasicServicesInteractor,
    QueryBasicServicesRequest,
)


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(QueryBasicServicesInteractor)

    def test_returns_empty_list_when_no_basic_services_exist(self) -> None:
        response = self.interactor.execute(self.make_request())
        assert not response.results

    def test_returns_all_services_when_no_filter_applied(self) -> None:
        member = self.member_generator.create_member()
        self.basic_service_generator.create_basic_service(member=member)
        self.basic_service_generator.create_basic_service(member=member)
        response = self.interactor.execute(self.make_request())
        assert len(response.results) == 2

    def test_filters_by_name_substring(self) -> None:
        member = self.member_generator.create_member()
        self.basic_service_generator.create_basic_service(member=member, name="Haircut")
        self.basic_service_generator.create_basic_service(
            member=member, name="Plumbing"
        )
        response = self.interactor.execute(self.make_request(query="Hair"))
        assert len(response.results) == 1
        assert response.results[0].name == "Haircut"

    def test_filter_is_case_insensitive(self) -> None:
        member = self.member_generator.create_member()
        self.basic_service_generator.create_basic_service(member=member, name="Haircut")
        response = self.interactor.execute(self.make_request(query="haircut"))
        assert len(response.results) == 1

    def test_returns_services_sorted_newest_first(self) -> None:
        self.datetime_service.freeze_time(datetime_utc(2026, 1, 1))
        member = self.member_generator.create_member()
        first_created = self.basic_service_generator.create_basic_service(
            member=member, name="Older"
        )
        self.datetime_service.advance_time(timedelta(days=1))
        second_created = self.basic_service_generator.create_basic_service(
            member=member, name="Newer"
        )
        response = self.interactor.execute(self.make_request())
        assert response.results[0].id == second_created
        assert response.results[1].id == first_created

    def test_total_results_reflects_filtered_count(self) -> None:
        member = self.member_generator.create_member()
        self.basic_service_generator.create_basic_service(member=member, name="Haircut")
        self.basic_service_generator.create_basic_service(
            member=member, name="Plumbing"
        )
        response = self.interactor.execute(self.make_request(query="Hair"))
        assert response.total_results == 1

    def test_total_results_equals_all_when_no_filter(self) -> None:
        member = self.member_generator.create_member()
        for _ in range(5):
            self.basic_service_generator.create_basic_service(member=member)
        response = self.interactor.execute(self.make_request())
        assert response.total_results == 5

    def test_limit_restricts_number_of_results(self) -> None:
        member = self.member_generator.create_member()
        for _ in range(10):
            self.basic_service_generator.create_basic_service(member=member)
        response = self.interactor.execute(self.make_request(limit=5))
        assert len(response.results) == 5

    def test_offset_skips_first_results(self) -> None:
        member = self.member_generator.create_member()
        for _ in range(10):
            self.basic_service_generator.create_basic_service(member=member)
        response = self.interactor.execute(self.make_request(offset=7))
        assert len(response.results) == 3

    def test_total_results_not_affected_by_pagination(self) -> None:
        member = self.member_generator.create_member()
        for _ in range(20):
            self.basic_service_generator.create_basic_service(member=member)
        response = self.interactor.execute(self.make_request(offset=15, limit=5))
        assert response.total_results == 20
        assert len(response.results) == 5

    def test_returns_correct_provider_name(self) -> None:
        member = self.member_generator.create_member(name="Alice")
        self.basic_service_generator.create_basic_service(member=member)
        response = self.interactor.execute(self.make_request())
        assert response.results[0].provider_name == "Alice"

    def test_returns_correct_service_name(self) -> None:
        member = self.member_generator.create_member()
        self.basic_service_generator.create_basic_service(member=member, name="Haircut")
        response = self.interactor.execute(self.make_request())
        assert response.results[0].name == "Haircut"

    def test_returns_correct_description(self) -> None:
        member = self.member_generator.create_member()
        self.basic_service_generator.create_basic_service(
            member=member, description="Professional haircut"
        )
        response = self.interactor.execute(self.make_request())
        assert response.results[0].description == "Professional haircut"

    def test_returns_correct_creation_timestamp(self) -> None:
        expected_time = datetime_utc(2026, 3, 22, 12, 0)
        self.datetime_service.freeze_time(expected_time)
        member = self.member_generator.create_member()
        self.basic_service_generator.create_basic_service(member=member)
        response = self.interactor.execute(self.make_request())
        assert response.results[0].created_on == expected_time

    def test_returns_correct_service_id(self) -> None:
        member = self.member_generator.create_member()
        expected_id = self.basic_service_generator.create_basic_service(member=member)
        response = self.interactor.execute(self.make_request())
        assert response.results[0].id == expected_id

    def test_no_results_when_query_matches_nothing(self) -> None:
        member = self.member_generator.create_member()
        self.basic_service_generator.create_basic_service(member=member, name="Haircut")
        response = self.interactor.execute(self.make_request(query="xyz"))
        assert len(response.results) == 0
        assert response.total_results == 0

    def test_includes_services_from_different_providers(self) -> None:
        member1 = self.member_generator.create_member()
        member2 = self.member_generator.create_member()
        self.basic_service_generator.create_basic_service(member=member1)
        self.basic_service_generator.create_basic_service(member=member2)
        response = self.interactor.execute(self.make_request())
        assert len(response.results) == 2

    def make_request(
        self,
        query: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> QueryBasicServicesRequest:
        return QueryBasicServicesRequest(
            query_string=query,
            offset=offset,
            limit=limit,
        )
