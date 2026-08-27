from uuid import UUID

from tests.datetime_service import datetime_utc
from tests.db.base_test_case import DatabaseTestCase
from workers_control.core.records import CoordinationTransferRequest


class CoordinationTransferRequestResultTests(DatabaseTestCase):
    def test_that_a_priori_no_coordination_transfer_requests_are_in_db(
        self,
    ) -> None:
        coordination_transfer_request_results = (
            self.database_gateway.get_coordination_transfer_requests()
        )
        assert not coordination_transfer_request_results

    def test_that_there_is_at_least_one_coordination_transfer_request_after_creating_one(
        self,
    ) -> None:
        self.database_gateway.create_coordination_transfer_request(
            requesting_coordination_tenure=self.coordination_tenure_generator.create_coordination_tenure(),
            candidate=self.company_generator.create_company(),
            request_date=self.datetime_service.now(),
        )
        coordination_transfer_request_results = (
            self.database_gateway.get_coordination_transfer_requests()
        )
        assert coordination_transfer_request_results

    def test_that_created_coordination_transfer_request_has_correct_properties_assigned(
        self,
    ) -> None:
        expected_requesting_coordination_tenure = (
            self.coordination_tenure_generator.create_coordination_tenure()
        )
        expected_candidate = self.company_generator.create_company()
        expected_request_date = datetime_utc(2020, 5, 1)
        result = self.database_gateway.create_coordination_transfer_request(
            requesting_coordination_tenure=expected_requesting_coordination_tenure,
            candidate=expected_candidate,
            request_date=expected_request_date,
        )
        assert (
            result.requesting_coordination_tenure
            == expected_requesting_coordination_tenure
        )
        assert result.candidate == expected_candidate
        assert result.request_date == expected_request_date

    def test_that_freshly_created_coordination_transfer_request_can_be_queried_by_id(
        self,
    ) -> None:
        coordination_transfer_request = self.create_coordination_transfer_request()
        coordination_transfer_request_results = (
            self.database_gateway.get_coordination_transfer_requests()
        )
        assert coordination_transfer_request_results.with_id(
            coordination_transfer_request.id
        )

    def test_that_results_filtered_by_id_dont_contain_coordination_transfer_requests_with_different_id(
        self,
    ) -> None:
        coordination_transfer_request = self.create_coordination_transfer_request()
        other_coordination_transfer_request = (
            self.create_coordination_transfer_request()
        )
        results = self.database_gateway.get_coordination_transfer_requests()
        assert other_coordination_transfer_request not in list(
            results.with_id(coordination_transfer_request.id)
        )

    def create_coordination_transfer_request(self) -> CoordinationTransferRequest:
        return self.database_gateway.create_coordination_transfer_request(
            requesting_coordination_tenure=self.coordination_tenure_generator.create_coordination_tenure(),
            candidate=self.company_generator.create_company(),
            request_date=self.datetime_service.now(),
        )


class RequestedByCoordinationTenureTests(DatabaseTestCase):
    def test_results_filtered_by_requesting_coordination_tenure_does_return_transfer_request_of_that_coordination_tenure(
        self,
    ) -> None:
        coordination_tenure = (
            self.coordination_tenure_generator.create_coordination_tenure()
        )
        transfer_request = self.create_coordination_transfer_request(
            requesting_coordination_tenure=coordination_tenure,
        )
        results = self.database_gateway.get_coordination_transfer_requests()
        assert transfer_request in list(results.requested_by(coordination_tenure))

    def test_results_filtered_by_requesting_coordination_tenure_dont_include_transfer_request_of_other_coordination_tenure(
        self,
    ) -> None:
        coordination_tenure = (
            self.coordination_tenure_generator.create_coordination_tenure()
        )
        other_coordination_tenure = (
            self.coordination_tenure_generator.create_coordination_tenure()
        )
        transfer_request = self.create_coordination_transfer_request(
            requesting_coordination_tenure=coordination_tenure,
        )
        other_transfer_request = self.create_coordination_transfer_request(
            requesting_coordination_tenure=other_coordination_tenure,
        )
        results = self.database_gateway.get_coordination_transfer_requests()
        assert transfer_request in list(results.requested_by(coordination_tenure))
        assert other_transfer_request not in list(
            results.requested_by(coordination_tenure)
        )

    def create_coordination_transfer_request(
        self, requesting_coordination_tenure: UUID
    ) -> CoordinationTransferRequest:
        if requesting_coordination_tenure is None:
            requesting_coordination_tenure = (
                self.coordination_tenure_generator.create_coordination_tenure()
            )
        return self.database_gateway.create_coordination_transfer_request(
            requesting_coordination_tenure=requesting_coordination_tenure,
            candidate=self.company_generator.create_company(),
            request_date=self.datetime_service.now(),
        )


class JoinedWithCollaborationTests(DatabaseTestCase):
    def test_that_joining_with_collaboration_returns_the_collaboration_from_which_the_request_has_been_issued(
        self,
    ) -> None:
        expected_collaboration = self.collaboration_generator.create_collaboration()
        coordination_tenure = (
            self.coordination_tenure_generator.create_coordination_tenure(
                collaboration=expected_collaboration,
            )
        )
        self.create_coordination_transfer_request(
            requesting_coordination_tenure=coordination_tenure,
        )
        results = (
            self.database_gateway.get_coordination_transfer_requests().joined_with_collaboration()
        )
        assert len(results) == 1
        transfer_request_and_collaboration = results.first()
        assert transfer_request_and_collaboration
        assert transfer_request_and_collaboration[1].id == expected_collaboration

    def test_that_joining_with_collaboration_does_not_return_another_existing_collaboration(
        self,
    ) -> None:
        expected_collaboration = self.collaboration_generator.create_collaboration()
        other_collaboration = self.collaboration_generator.create_collaboration()
        coordination_tenure = (
            self.coordination_tenure_generator.create_coordination_tenure(
                collaboration=expected_collaboration,
            )
        )
        self.create_coordination_transfer_request(
            requesting_coordination_tenure=coordination_tenure,
        )
        results = (
            self.database_gateway.get_coordination_transfer_requests().joined_with_collaboration()
        )
        assert len(results) == 1
        transfer_request_and_collaboration = results.first()
        assert transfer_request_and_collaboration
        assert transfer_request_and_collaboration[1].id != other_collaboration

    def test_correct_collaboration_gets_retrieved_when_from_two_collaborations_transfer_requests_have_been_issued(
        self,
    ) -> None:
        expected_collaboration = self.collaboration_generator.create_collaboration()
        other_collaboration = self.collaboration_generator.create_collaboration()
        coordination_tenure = (
            self.coordination_tenure_generator.create_coordination_tenure(
                collaboration=expected_collaboration,
            )
        )
        other_coordination_tenure = (
            self.coordination_tenure_generator.create_coordination_tenure(
                collaboration=other_collaboration,
            )
        )
        expected_transfer_request = self.create_coordination_transfer_request(
            requesting_coordination_tenure=coordination_tenure,
        )
        self.create_coordination_transfer_request(
            requesting_coordination_tenure=other_coordination_tenure,
        )
        results = (
            self.database_gateway.get_coordination_transfer_requests().joined_with_collaboration()
        )
        assert len(results) == 2
        for transfer_request, collaboration in results:
            if transfer_request.id == expected_transfer_request.id:
                assert collaboration.id == expected_collaboration
            else:
                assert collaboration.id == other_collaboration

    def create_coordination_transfer_request(
        self, requesting_coordination_tenure: UUID
    ) -> CoordinationTransferRequest:
        if requesting_coordination_tenure is None:
            requesting_coordination_tenure = (
                self.coordination_tenure_generator.create_coordination_tenure()
            )
        return self.database_gateway.create_coordination_transfer_request(
            requesting_coordination_tenure=requesting_coordination_tenure,
            candidate=self.company_generator.create_company(),
            request_date=self.datetime_service.now(),
        )
