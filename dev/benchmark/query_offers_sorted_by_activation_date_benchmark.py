import random
from decimal import Decimal

from dev.benchmark.dependency_injection import benchmark_injector
from tests.data_generators import CollaborationGenerator, PlanGenerator
from tests.db.base_test_case import reset_test_db
from workers_control.core.interactors import query_offers
from workers_control.core.records import ProductionCosts
from workers_control.db.db import Database


class QueryOffersSortedByActivationDateBenchmark:
    def __init__(self) -> None:
        self.injector = benchmark_injector
        reset_test_db()
        self.db = self.injector.get(Database)

        plan_generator = self.injector.get(PlanGenerator)
        collaboration_generator = self.injector.get(CollaborationGenerator)
        self.query_offers = self.injector.get(query_offers.QueryOffersInteractor)
        random.seed()
        for _ in range(500):
            plan_generator.create_plan(
                is_public_service=True, costs=self.random_production_costs()
            )
        for _ in range(500):
            plan_generator.create_plan(
                is_public_service=False, costs=self.random_production_costs()
            )
        for _ in range(100):
            collaboration = collaboration_generator.create_collaboration()
            for _ in range(5):
                plan_generator.create_plan(
                    collaboration=collaboration, costs=self.random_production_costs()
                )
        self.request = query_offers.QueryOffersRequest(
            query_string=None,
            filter_category=query_offers.OfferFilter.by_offer_name,
            sorting_category=query_offers.OfferSorting.by_activation,
            include_expired_plans=False,
            include_basic_services=False,
            limit=None,
            offset=None,
        )
        self.db.session.flush()

    def tear_down(self) -> None:
        self.db.session.remove()

    def run(self) -> None:
        self.query_offers.execute(self.request)

    def random_production_costs(self) -> ProductionCosts:
        return ProductionCosts(
            labour_cost=Decimal(random.randrange(0, 1000)),
            means_cost=Decimal(random.randrange(0, 1000)),
            resource_cost=Decimal(random.randrange(0, 1000)),
        )
