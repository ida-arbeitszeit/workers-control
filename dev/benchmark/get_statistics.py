import random
from decimal import Decimal

from tests.data_generators import PlanGenerator
from tests.db.base_test_case import reset_test_db
from tests.db.dependency_injection import DatabaseTestModule
from tests.dependency_injection import TestingModule
from workers_control.core.injector import Injector
from workers_control.core.interactors import get_statistics
from workers_control.core.records import ProductionCosts
from workers_control.db.db import Database


class GetStatisticsBenchmark:
    def __init__(self) -> None:
        self.injector = Injector([TestingModule(), DatabaseTestModule()])
        reset_test_db()
        self.db = self.injector.get(Database)
        self.db.engine.dispose()

        plan_generator = self.injector.get(PlanGenerator)
        self.get_statistics_interactor = self.injector.get(
            get_statistics.GetStatisticsInteractor
        )
        random.seed()
        for _ in range(500):
            plan_generator.create_plan(
                is_public_service=True, costs=self.random_production_costs()
            )
        for _ in range(500):
            plan_generator.create_plan(
                is_public_service=False, costs=self.random_production_costs()
            )
        self.db.session.flush()

    def tear_down(self) -> None:
        self.db.session.remove()

    def run(self) -> None:
        self.get_statistics_interactor.get_statistics()

    def random_production_costs(self) -> ProductionCosts:
        return ProductionCosts(
            labour_cost=Decimal(random.randrange(0, 1000)),
            means_cost=Decimal(random.randrange(0, 1000)),
            resource_cost=Decimal(random.randrange(0, 1000)),
        )
