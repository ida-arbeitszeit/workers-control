from datetime import timedelta
from uuid import uuid4

from tests.datetime_service import datetime_utc
from tests.db.base_test_case import DatabaseTestCase
from workers_control.core.records import Collaboration


class CollaborationResultTests(DatabaseTestCase):
    def test_that_a_priori_no_collaborations_are_in_db(self) -> None:
        collaborations = self.database_gateway.get_collaborations()
        assert not collaborations

    def test_that_there_is_at_least_one_collaboration_after_creating_one(self) -> None:
        self.database_gateway.create_collaboration(
            name="",
            definition="",
            creation_timestamp=datetime_utc(2000, 1, 1),
            account=self.database_gateway.create_account().id,
        )
        collaborations = self.database_gateway.get_collaborations()
        assert collaborations

    def test_that_created_collaboration_has_correct_properties_assigned(self) -> None:
        expected_name = "expected_name"
        expected_definition = "expected definition"
        expected_creation_timestamp = datetime_utc(2345, 1, 12)
        expected_account = self.database_gateway.create_account().id
        collaboration = self.database_gateway.create_collaboration(
            name=expected_name,
            definition=expected_definition,
            creation_timestamp=expected_creation_timestamp,
            account=expected_account,
        )
        assert collaboration.name == expected_name
        assert collaboration.definition == expected_definition
        assert collaboration.creation_date == expected_creation_timestamp
        assert collaboration.account == expected_account

    def test_that_freshly_created_collaboration_can_be_queried_by_id(self) -> None:
        collaboration = self.create_collaboration()
        collaborations = self.database_gateway.get_collaborations()
        assert collaborations.with_id(collaboration.id)

    def test_that_results_filtered_by_id_dont_contain_collabs_with_different_id(
        self,
    ) -> None:
        collaboration = self.create_collaboration()
        other_collaboration = self.create_collaboration()
        collaborations = self.database_gateway.get_collaborations()
        assert other_collaboration not in list(collaborations.with_id(collaboration.id))

    def test_results_filtered_by_name_include_collaborations_with_exact_match(
        self,
    ) -> None:
        expected_name = "expected collab name"
        self.create_collaboration(name=expected_name)
        collaborations = self.database_gateway.get_collaborations()
        assert collaborations.with_name_ignoring_case(expected_name)

    def test_results_filtered_by_name_dont_include_collabs_where_query_is_only_a_substring(
        self,
    ) -> None:
        collab_name = "collab name"
        self.create_collaboration(name=collab_name)
        collaborations = self.database_gateway.get_collaborations()
        assert not collaborations.with_name_ignoring_case(collab_name[:-1])

    def test_results_filtered_by_name_include_collabs_with_differing_case(
        self,
    ) -> None:
        collab_name = "collab name"
        self.create_collaboration(name=collab_name)
        collaborations = self.database_gateway.get_collaborations()
        assert collaborations.with_name_ignoring_case(collab_name.upper())

    def create_collaboration(self, name: str = "test name") -> Collaboration:
        return self.database_gateway.create_collaboration(
            name=name,
            definition="",
            creation_timestamp=datetime_utc(2000, 1, 1),
            account=self.database_gateway.create_account().id,
        )


class CoordinatedByCompanyTests(DatabaseTestCase):
    def test_results_filtered_by_coordinator_includes_previously_created_collab_by_coordinator(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        coordinator = self.company_generator.create_company()
        collaboration = self.collaboration_generator.create_collaboration()
        self.database_gateway.create_coordination_tenure(
            company=coordinator,
            collaboration=collaboration,
            start_date=datetime_utc(2000, 1, 2),
        )
        collaborations = self.database_gateway.get_collaborations()
        assert collaborations.coordinated_by_company(coordinator)

    def test_with_two_collaborations_with_two_tenures_each_by_the_same_coordinator_we_receive_two_results(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        coordinator = self.company_generator.create_company()
        collab_1 = self.collaboration_generator.create_collaboration(
            coordinator=coordinator
        )
        collab_2 = self.collaboration_generator.create_collaboration(
            coordinator=coordinator
        )
        tenure_start_date = datetime_utc(2000, 1, 2)
        self.database_gateway.create_coordination_tenure(
            company=coordinator, collaboration=collab_1, start_date=tenure_start_date
        )
        self.database_gateway.create_coordination_tenure(
            company=coordinator, collaboration=collab_2, start_date=tenure_start_date
        )
        assert (
            len(
                self.database_gateway.get_collaborations().coordinated_by_company(
                    coordinator
                )
            )
            == 2
        )

    def test_results_filtered_by_coordinator_dont_include_collab_by_other_coordinator(
        self,
    ) -> None:
        coordinator = self.company_generator.create_company()
        other_company = self.company_generator.create_company()
        collaboration = self.collaboration_generator.create_collaboration()
        self.database_gateway.create_coordination_tenure(
            company=coordinator,
            collaboration=collaboration,
            start_date=datetime_utc(2000, 1, 1),
        )
        collaborations = self.database_gateway.get_collaborations()
        assert not collaborations.coordinated_by_company(other_company)


class OfPlanTests(DatabaseTestCase):
    def test_that_no_collaborations_are_yielded_if_plan_does_not_exist(self) -> None:
        collaborations = self.database_gateway.get_collaborations()
        assert not collaborations.of_plan(uuid4())

    def test_that_no_collaborations_are_yielded_if_plan_is_not_part_of_collaboration(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        self.collaboration_generator.create_collaboration()
        collaborations = self.database_gateway.get_collaborations()
        assert not collaborations.of_plan(plan)

    def test_that_collaboration_of_plan_is_yielded(self) -> None:
        plan = self.plan_generator.create_plan()
        collaboration = self.collaboration_generator.create_collaboration(plans=[plan])
        self.collaboration_generator.create_collaboration()  # other collaboration
        collaborations = self.database_gateway.get_collaborations()
        result = collaborations.of_plan(plan).first()
        assert result
        assert result.id == collaboration


class JoinedWithCurrentCoordinatorTests(DatabaseTestCase):
    def test_that_joining_with_current_coordinator_yields_the_current_coordinator_of_a_collab(
        self,
    ) -> None:
        expected_coordinator_name = "test coordinator"
        coordinator_id = self.company_generator.create_company(
            name=expected_coordinator_name
        )
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        collab = self.collaboration_generator.create_collaboration(
            coordinator=coordinator_id
        )
        self.datetime_service.advance_time(timedelta(days=1))
        expected_coordination = self.database_gateway.create_coordination_tenure(
            company=coordinator_id,
            collaboration=collab,
            start_date=self.datetime_service.now(),
        )
        collaborations = self.database_gateway.get_collaborations()
        result = collaborations.joined_with_current_coordinator().first()
        assert result is not None
        _, coordinator = result
        assert coordinator.id == coordinator_id
        assert coordinator.id == expected_coordination.company
        assert coordinator.name == expected_coordinator_name

    def test_that_can_have_multiple_collaborations_in_result_set(self) -> None:
        self.collaboration_generator.create_collaboration()
        self.collaboration_generator.create_collaboration()
        self.collaboration_generator.create_collaboration()
        assert (
            len(
                self.database_gateway.get_collaborations().joined_with_current_coordinator()
            )
            == 3
        )

    def test_for_one_collaboration_get_one_result_when_tenure_changed_once(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        new_coordinator = self.company_generator.create_company()
        collaboration = self.collaboration_generator.create_collaboration()
        self.database_gateway.create_coordination_tenure(
            company=new_coordinator,
            collaboration=collaboration,
            start_date=datetime_utc(2000, 1, 2),
        )
        assert (
            len(
                self.database_gateway.get_collaborations().joined_with_current_coordinator()
            )
            == 1
        )
