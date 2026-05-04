from tests.datetime_service import datetime_utc
from tests.db.base_test_case import DatabaseTestCase


class BasicServiceResultTests(DatabaseTestCase):
    def test_that_a_priori_no_basic_services_are_in_db(self) -> None:
        basic_services = self.database_gateway.get_basic_services()
        assert not basic_services

    def test_that_there_is_at_least_one_basic_service_after_creating_one(self) -> None:
        member = self.member_generator.create_member()
        self.database_gateway.create_basic_service(
            name="test service",
            description="test description",
            provider=member,
            created_on=datetime_utc(2000, 1, 1),
        )
        basic_services = self.database_gateway.get_basic_services()
        assert basic_services

    def test_that_created_basic_service_has_correct_name(self) -> None:
        member = self.member_generator.create_member()
        expected_name = "expected name"
        service = self.database_gateway.create_basic_service(
            name=expected_name,
            description="description",
            provider=member,
            created_on=datetime_utc(2000, 1, 1),
        )
        assert service.name == expected_name

    def test_that_created_basic_service_has_correct_description(self) -> None:
        member = self.member_generator.create_member()
        expected_description = "expected description"
        service = self.database_gateway.create_basic_service(
            name="name",
            description=expected_description,
            provider=member,
            created_on=datetime_utc(2000, 1, 1),
        )
        assert service.description == expected_description

    def test_that_created_basic_service_has_correct_provider(self) -> None:
        member = self.member_generator.create_member()
        service = self.database_gateway.create_basic_service(
            name="name",
            description="description",
            provider=member,
            created_on=datetime_utc(2000, 1, 1),
        )
        assert service.provider == member

    def test_that_created_basic_service_has_correct_created_on(self) -> None:
        member = self.member_generator.create_member()
        expected_timestamp = datetime_utc(2025, 6, 15, 12, 30)
        service = self.database_gateway.create_basic_service(
            name="name",
            description="description",
            provider=member,
            created_on=expected_timestamp,
        )
        assert service.created_on == expected_timestamp

    def test_that_freshly_created_basic_service_can_be_queried_by_id(self) -> None:
        member = self.member_generator.create_member()
        service = self.database_gateway.create_basic_service(
            name="name",
            description="description",
            provider=member,
            created_on=datetime_utc(2000, 1, 1),
        )
        result = self.database_gateway.get_basic_services().with_id(service.id).first()
        assert result
        assert result == service

    def test_that_results_filtered_by_id_dont_contain_services_with_different_id(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        service = self.database_gateway.create_basic_service(
            name="name",
            description="description",
            provider=member,
            created_on=datetime_utc(2000, 1, 1),
        )
        other_service = self.database_gateway.create_basic_service(
            name="other",
            description="other description",
            provider=member,
            created_on=datetime_utc(2000, 1, 2),
        )
        results = list(self.database_gateway.get_basic_services().with_id(service.id))
        assert other_service not in results

    def test_that_results_filtered_by_provider_include_services_of_that_member(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        self.database_gateway.create_basic_service(
            name="name",
            description="description",
            provider=member,
            created_on=datetime_utc(2000, 1, 1),
        )
        results = self.database_gateway.get_basic_services().of_provider(member)
        assert results

    def test_that_results_filtered_by_provider_dont_include_services_of_other_member(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        other_member = self.member_generator.create_member()
        self.database_gateway.create_basic_service(
            name="name",
            description="description",
            provider=member,
            created_on=datetime_utc(2000, 1, 1),
        )
        results = self.database_gateway.get_basic_services().of_provider(other_member)
        assert not results

    def test_with_name_containing_returns_matching_service(self) -> None:
        member = self.member_generator.create_member()
        self.database_gateway.create_basic_service(
            name="Haircut",
            description="description",
            provider=member,
            created_on=datetime_utc(2000, 1, 1),
        )
        results = self.database_gateway.get_basic_services().with_name_containing(
            "Hair"
        )
        assert len(results) == 1

    def test_with_name_containing_excludes_non_matching_service(self) -> None:
        member = self.member_generator.create_member()
        self.database_gateway.create_basic_service(
            name="Plumbing",
            description="description",
            provider=member,
            created_on=datetime_utc(2000, 1, 1),
        )
        results = self.database_gateway.get_basic_services().with_name_containing(
            "Hair"
        )
        assert not results

    def test_with_name_containing_is_case_insensitive(self) -> None:
        member = self.member_generator.create_member()
        self.database_gateway.create_basic_service(
            name="Haircut",
            description="description",
            provider=member,
            created_on=datetime_utc(2000, 1, 1),
        )
        results = self.database_gateway.get_basic_services().with_name_containing(
            "haircut"
        )
        assert len(results) == 1

    def test_ordered_by_creation_date_ascending(self) -> None:
        member = self.member_generator.create_member()
        older = self.database_gateway.create_basic_service(
            name="older",
            description="description",
            provider=member,
            created_on=datetime_utc(2000, 1, 1),
        )
        newer = self.database_gateway.create_basic_service(
            name="newer",
            description="description",
            provider=member,
            created_on=datetime_utc(2000, 1, 2),
        )
        results = list(
            self.database_gateway.get_basic_services().ordered_by_creation_date(
                ascending=True
            )
        )
        assert results[0].id == older.id
        assert results[1].id == newer.id

    def test_ordered_by_creation_date_descending(self) -> None:
        member = self.member_generator.create_member()
        older = self.database_gateway.create_basic_service(
            name="older",
            description="description",
            provider=member,
            created_on=datetime_utc(2000, 1, 1),
        )
        newer = self.database_gateway.create_basic_service(
            name="newer",
            description="description",
            provider=member,
            created_on=datetime_utc(2000, 1, 2),
        )
        results = list(
            self.database_gateway.get_basic_services().ordered_by_creation_date(
                ascending=False
            )
        )
        assert results[0].id == newer.id
        assert results[1].id == older.id

    def test_joined_with_provider_returns_correct_member(self) -> None:
        member = self.member_generator.create_member(name="Alice")
        self.database_gateway.create_basic_service(
            name="service",
            description="description",
            provider=member,
            created_on=datetime_utc(2000, 1, 1),
        )
        results = list(
            self.database_gateway.get_basic_services().joined_with_provider()
        )
        assert len(results) == 1
        basic_service, provider = results[0]
        assert provider.name == "Alice"
        assert basic_service.name == "service"

    def test_joined_with_provider_returns_multiple_results(self) -> None:
        member1 = self.member_generator.create_member(name="Alice")
        member2 = self.member_generator.create_member(name="Bob")
        self.database_gateway.create_basic_service(
            name="service1",
            description="description",
            provider=member1,
            created_on=datetime_utc(2000, 1, 1),
        )
        self.database_gateway.create_basic_service(
            name="service2",
            description="description",
            provider=member2,
            created_on=datetime_utc(2000, 1, 2),
        )
        results = list(
            self.database_gateway.get_basic_services().joined_with_provider()
        )
        assert len(results) == 2

    def test_freshly_created_basic_service_has_no_deactivation_timestamp(self) -> None:
        member = self.member_generator.create_member()
        service = self.database_gateway.create_basic_service(
            name="name",
            description="description",
            provider=member,
            created_on=datetime_utc(2000, 1, 1),
        )
        assert service.deactivated_on is None

    def test_that_are_active_includes_freshly_created_services(self) -> None:
        member = self.member_generator.create_member()
        self.database_gateway.create_basic_service(
            name="name",
            description="description",
            provider=member,
            created_on=datetime_utc(2000, 1, 1),
        )
        assert self.database_gateway.get_basic_services().that_are_active()

    def test_that_are_active_excludes_deactivated_services(self) -> None:
        member = self.member_generator.create_member()
        service = self.database_gateway.create_basic_service(
            name="name",
            description="description",
            provider=member,
            created_on=datetime_utc(2000, 1, 1),
        )
        self.database_gateway.get_basic_services().with_id(
            service.id
        ).update().set_deactivated_on(datetime_utc(2000, 6, 1)).perform()
        assert not self.database_gateway.get_basic_services().that_are_active()

    def test_set_deactivated_on_persists_timestamp(self) -> None:
        member = self.member_generator.create_member()
        service = self.database_gateway.create_basic_service(
            name="name",
            description="description",
            provider=member,
            created_on=datetime_utc(2000, 1, 1),
        )
        expected = datetime_utc(2026, 5, 3, 9, 30)
        self.database_gateway.get_basic_services().with_id(
            service.id
        ).update().set_deactivated_on(expected).perform()
        reloaded = (
            self.database_gateway.get_basic_services().with_id(service.id).first()
        )
        assert reloaded is not None
        assert reloaded.deactivated_on == expected

    def test_set_deactivated_on_returns_number_of_affected_rows(self) -> None:
        member = self.member_generator.create_member()
        for _ in range(3):
            self.database_gateway.create_basic_service(
                name="name",
                description="description",
                provider=member,
                created_on=datetime_utc(2000, 1, 1),
            )
        affected = (
            self.database_gateway.get_basic_services()
            .of_provider(member)
            .update()
            .set_deactivated_on(datetime_utc(2026, 5, 3))
            .perform()
        )
        assert affected == 3
