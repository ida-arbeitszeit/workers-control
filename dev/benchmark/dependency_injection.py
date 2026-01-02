from tests.db.dependency_injection import DatabaseTestModule
from tests.dependency_injection import TestingModule
from workers_control.core.injector import Injector

benchmark_injector = Injector([TestingModule(), DatabaseTestModule()])
