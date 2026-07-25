from typing import Union
from uuid import UUID, uuid4

from tests.interactors.base_test_case import BaseTestCase
from workers_control.core.interactors import list_workers
from workers_control.core.records import Member


class ListWorkersTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(list_workers.ListWorkersInteractor)

    @classmethod
    def make_request(cls, company: UUID) -> list_workers.Request:
        return list_workers.Request(company)

    @classmethod
    def worker_in_results(
        cls, worker: Union[Member, UUID], response: list_workers.Response
    ) -> bool:
        if isinstance(worker, Member):
            worker = worker.id
        return any(w.id == worker for w in response.workers)

    def test_list_workers_response_is_empty_for_nonexisting_company(
        self,
    ) -> None:
        response: list_workers.Response = self.interactor.execute(
            self.make_request(company=uuid4())
        )
        assert not response.workers

    def test_list_workers_response_is_empty_for_company_without_worker(self) -> None:
        company = self.company_generator.create_company()
        response = self.interactor.execute(self.make_request(company=company))
        assert not response.workers

    def test_list_workers_response_includes_single_company_worker(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        response = self.interactor.execute(self.make_request(company=company))
        assert self.worker_in_results(worker, response)

    def test_list_workers_response_includes_multiple_company_workers(self) -> None:
        worker1 = self.member_generator.create_member()
        worker2 = self.member_generator.create_member()
        company = self.company_generator.create_company_record(
            workers=[worker1, worker2]
        )
        response: list_workers.Response = self.interactor.execute(
            self.make_request(company=company.id)
        )
        assert self.worker_in_results(worker1, response) and self.worker_in_results(
            worker2, response
        )
