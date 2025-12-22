import enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal

from parameterized import parameterized

from arbeitszeit.records import ProductionCosts
from arbeitszeit.services.payout_factor import PayoutFactorService
from tests.interactors.base_test_case import BaseTestCase
from tests.payout_factor import PayoutFactorConfigTestImpl

DEFAULT_COSTS = ProductionCosts(
    means_cost=Decimal(1), resource_cost=Decimal(1), labour_cost=Decimal(1)
)
HIGHER_COSTS = ProductionCosts(
    means_cost=Decimal(5), resource_cost=Decimal(5), labour_cost=Decimal(5)
)


class PlanPosition(enum.Enum):
    """
    The plan's position on a timeline relative to a gliding window's borders.
    """

    out_left = enum.auto()
    out_left_one_half = enum.auto()
    inside = enum.auto()
    out_right_one_half = enum.auto()
    out_right = enum.auto()


@dataclass
class PlanConfig:
    position: PlanPosition
    is_public: bool = False
    costs: ProductionCosts = field(default_factory=lambda: DEFAULT_COSTS)


@dataclass
class OnePlanTestCase:
    plan: PlanConfig
    expected_fic: Decimal


@dataclass
class TwoPlanTestCase:
    plan_1: PlanConfig
    plan_2: PlanConfig
    expected_fic: Decimal


ONE_PLAN_TEST_CASES = [
    OnePlanTestCase(
        PlanConfig(
            position=PlanPosition.out_left,
        ),
        Decimal(1),
    ),
    OnePlanTestCase(
        PlanConfig(
            is_public=True,
            position=PlanPosition.out_left,
        ),
        Decimal(1),
    ),
    OnePlanTestCase(
        PlanConfig(
            position=PlanPosition.out_left_one_half,
        ),
        Decimal(1),
    ),
    OnePlanTestCase(
        PlanConfig(
            is_public=True,
            position=PlanPosition.out_left_one_half,
        ),
        Decimal(0),
    ),
    OnePlanTestCase(
        PlanConfig(
            position=PlanPosition.inside,
        ),
        Decimal(1),
    ),
    OnePlanTestCase(
        PlanConfig(
            is_public=True,
            position=PlanPosition.inside,
        ),
        Decimal(0),
    ),
    OnePlanTestCase(
        PlanConfig(
            position=PlanPosition.out_right_one_half,
        ),
        Decimal(1),
    ),
    OnePlanTestCase(
        PlanConfig(
            is_public=True,
            position=PlanPosition.out_right_one_half,
        ),
        Decimal(0),
    ),
    OnePlanTestCase(
        PlanConfig(
            position=PlanPosition.out_right,
        ),
        Decimal(1),
    ),
    OnePlanTestCase(
        PlanConfig(
            is_public=True,
            position=PlanPosition.out_right,
        ),
        Decimal(0),
    ),
]


TWO_PLAN_TEST_CASES = [
    # TWO PLANS - ONE PRODUCTIVE AND ONE PUBLIC
    #
    # first plan left out
    # ===================
    # both plans with same costs
    # --------------------------
    TwoPlanTestCase(
        PlanConfig(
            position=PlanPosition.out_left,
        ),
        PlanConfig(
            is_public=True,
            position=PlanPosition.out_left,
        ),
        Decimal(1),
    ),
    TwoPlanTestCase(
        PlanConfig(position=PlanPosition.out_left),
        PlanConfig(
            is_public=True,
            position=PlanPosition.out_left_one_half,
        ),
        Decimal(0),
    ),
    TwoPlanTestCase(
        PlanConfig(position=PlanPosition.out_left),
        PlanConfig(
            is_public=True,
            position=PlanPosition.inside,
        ),
        Decimal(0),
    ),
    TwoPlanTestCase(
        PlanConfig(position=PlanPosition.out_left),
        PlanConfig(
            is_public=True,
            position=PlanPosition.out_right_one_half,
        ),
        Decimal(0),
    ),
    TwoPlanTestCase(
        PlanConfig(is_public=True, position=PlanPosition.out_left),
        PlanConfig(
            position=PlanPosition.out_left_one_half,
        ),
        Decimal(1),
    ),
    TwoPlanTestCase(
        PlanConfig(is_public=True, position=PlanPosition.out_left),
        PlanConfig(
            position=PlanPosition.inside,
        ),
        Decimal(1),
    ),
    TwoPlanTestCase(
        PlanConfig(is_public=True, position=PlanPosition.out_left),
        PlanConfig(
            position=PlanPosition.out_right_one_half,
        ),
        Decimal(1),
    ),
    # first plan out left one half
    # ============================
    # both plans with same costs
    # --------------------------
    TwoPlanTestCase(
        PlanConfig(position=PlanPosition.out_left_one_half),
        PlanConfig(is_public=True, position=PlanPosition.out_left_one_half),
        Decimal(0),
    ),
    TwoPlanTestCase(
        PlanConfig(position=PlanPosition.out_left_one_half),
        PlanConfig(is_public=True, position=PlanPosition.inside),
        Decimal(0),
    ),
    TwoPlanTestCase(
        PlanConfig(position=PlanPosition.out_left_one_half),
        PlanConfig(is_public=True, position=PlanPosition.out_right_one_half),
        Decimal(0),
    ),
    TwoPlanTestCase(
        PlanConfig(is_public=True, position=PlanPosition.out_left_one_half),
        PlanConfig(position=PlanPosition.inside),
        Decimal(0),
    ),
    TwoPlanTestCase(
        PlanConfig(is_public=True, position=PlanPosition.out_left_one_half),
        PlanConfig(position=PlanPosition.out_right_one_half),
        Decimal(0),
    ),
    # productive plan has higher costs
    # ---------------------------------
    TwoPlanTestCase(
        PlanConfig(
            position=PlanPosition.out_left_one_half,
            costs=HIGHER_COSTS,
        ),
        PlanConfig(is_public=True, position=PlanPosition.out_left_one_half),
        Decimal(0.5),
    ),
    TwoPlanTestCase(
        PlanConfig(position=PlanPosition.out_left_one_half, costs=HIGHER_COSTS),
        PlanConfig(is_public=True, position=PlanPosition.inside),
        Decimal(1 / 7),
    ),
    TwoPlanTestCase(
        PlanConfig(position=PlanPosition.out_left_one_half, costs=HIGHER_COSTS),
        PlanConfig(is_public=True, position=PlanPosition.out_right_one_half),
        Decimal(0.5),
    ),
    TwoPlanTestCase(
        PlanConfig(is_public=True, position=PlanPosition.out_left_one_half),
        PlanConfig(position=PlanPosition.inside, costs=HIGHER_COSTS),
        Decimal(4 / 5.5),
    ),
    TwoPlanTestCase(
        PlanConfig(is_public=True, position=PlanPosition.out_left_one_half),
        PlanConfig(position=PlanPosition.out_right_one_half, costs=HIGHER_COSTS),
        Decimal(0.5),
    ),
    # first plan inside
    # ============================
    # both plans with same costs
    # --------------------------
    TwoPlanTestCase(
        PlanConfig(position=PlanPosition.inside),
        PlanConfig(is_public=True, position=PlanPosition.inside),
        Decimal(0),
    ),
    TwoPlanTestCase(
        PlanConfig(position=PlanPosition.inside),
        PlanConfig(is_public=True, position=PlanPosition.out_right_one_half),
        Decimal(0),
    ),
    TwoPlanTestCase(
        PlanConfig(is_public=True, position=PlanPosition.inside),
        PlanConfig(position=PlanPosition.out_right_one_half),
        Decimal(0),
    ),
    # productive plan has higher costs
    # ---------------------------------
    TwoPlanTestCase(
        PlanConfig(position=PlanPosition.inside, costs=HIGHER_COSTS),
        PlanConfig(is_public=True, position=PlanPosition.inside),
        Decimal(0.5),
    ),
    TwoPlanTestCase(
        PlanConfig(position=PlanPosition.inside, costs=HIGHER_COSTS),
        PlanConfig(is_public=True, position=PlanPosition.out_right_one_half),
        Decimal(4 / 5.5),
    ),
    TwoPlanTestCase(
        PlanConfig(is_public=True, position=PlanPosition.inside),
        PlanConfig(position=PlanPosition.out_right_one_half, costs=HIGHER_COSTS),
        Decimal(1 / 7),
    ),
    # both plans out right half
    # =========================
    # both plans with same costs
    # --------------------------
    TwoPlanTestCase(
        PlanConfig(position=PlanPosition.out_right_one_half),
        PlanConfig(is_public=True, position=PlanPosition.out_right_one_half),
        Decimal(0),
    ),
    # productive plan has higher costs
    # ---------------------------------
    TwoPlanTestCase(
        PlanConfig(position=PlanPosition.out_right_one_half, costs=HIGHER_COSTS),
        PlanConfig(is_public=True, position=PlanPosition.out_right_one_half),
        Decimal(0.5),
    ),
]


class PayoutFactorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.service = self.injector.get(PayoutFactorService)
        self.payout_factor_config = self.injector.get(PayoutFactorConfigTestImpl)

    def test_that_payout_factor_is_1_if_no_plans_exist(self) -> None:
        pf = self.service.calculate_current_payout_factor()
        assert pf == 1

    @parameterized.expand(
        [(tc.plan, tc.expected_fic) for tc in ONE_PLAN_TEST_CASES],
        name_func=lambda func, num, p: f"{func.__name__}__{'pub' if p.args[0].is_public else 'prod'}__{p.args[0].position.name}",
    )
    def test_payout_factor_calculation_with_one_plan(
        self,
        plan: PlanConfig,
        expected_payout_factor: Decimal,
    ) -> None:
        self._create_plan(plan)
        pf = self.service.calculate_current_payout_factor()
        self.assertAlmostEqual(pf, expected_payout_factor)

    @parameterized.expand(
        [(tc.plan_1, tc.plan_2, tc.expected_fic) for tc in TWO_PLAN_TEST_CASES],
        name_func=lambda func, num, p: f"{func.__name__}__{'pub' if p.args[0].is_public else 'prod'}_{p.args[0].position.name}__{'pub' if p.args[1].is_public else 'prod'}_{p.args[1].position.name}",
    )
    def test_payout_factor_calculation_with_two_plans(
        self,
        plan_1: PlanConfig,
        plan_2: PlanConfig,
        expected_payout_factor: Decimal,
    ) -> None:
        self._create_plan(plan_1)
        self._create_plan(plan_2)
        pf = self.service.calculate_current_payout_factor()
        self.assertAlmostEqual(pf, expected_payout_factor)

    def test_that_pf_decreases_with_increasing_calculation_window_if_public_plan_lasts_longer_than_productive_plan(
        self,
    ) -> None:
        # shorter productive plan
        self.plan_generator.create_plan(costs=HIGHER_COSTS, timeframe=1)
        # longer public plan
        self.plan_generator.create_plan(
            costs=DEFAULT_COSTS, timeframe=10, is_public_service=True
        )

        self.payout_factor_config.set_window_length(2)
        pf_short = self.service.calculate_current_payout_factor()
        self.payout_factor_config.set_window_length(10)
        pf_long = self.service.calculate_current_payout_factor()

        assert pf_long < pf_short

    def test_that_pf_increases_with_increasing_calculation_window_if_productive_plan_lasts_longer_than_public_plan(
        self,
    ) -> None:
        # longer productive plan
        self.plan_generator.create_plan(costs=HIGHER_COSTS, timeframe=10)
        # shorter public plan
        self.plan_generator.create_plan(
            costs=DEFAULT_COSTS, timeframe=1, is_public_service=True
        )

        self.payout_factor_config.set_window_length(2)
        pf_short = self.service.calculate_current_payout_factor()
        self.payout_factor_config.set_window_length(10)
        pf_long = self.service.calculate_current_payout_factor()
        assert pf_long > pf_short

    def _create_plan(self, plan: PlanConfig) -> None:
        now = datetime(2025, 12, 1)
        self.datetime_service.freeze_time(now)
        duration, start = self._calculate_plan_duration_and_plan_start(plan.position)
        self.datetime_service.freeze_time(start)
        self.plan_generator.create_plan(
            is_public_service=plan.is_public,
            costs=plan.costs,
            timeframe=duration,
        )
        self.datetime_service.freeze_time(now)

    def _calculate_plan_duration_and_plan_start(
        self, plan_position: PlanPosition
    ) -> tuple[int, datetime]:
        window_size = self.payout_factor_config.get_window_length_in_days()
        now = self.datetime_service.now()
        match plan_position:
            case PlanPosition.out_left:
                plan_duration = window_size
                plan_start = now - timedelta(days=window_size * 3)
            case PlanPosition.out_left_one_half:
                plan_duration = window_size
                plan_start = now - timedelta(days=window_size)
            case PlanPosition.inside:
                plan_duration = window_size // 4
                plan_start = now
            case PlanPosition.out_right_one_half:
                plan_duration = window_size
                plan_start = now
            case PlanPosition.out_right:
                plan_duration = window_size * 2
                plan_start = now - timedelta(days=window_size)
        return int(plan_duration), plan_start
