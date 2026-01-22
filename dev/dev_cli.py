from decimal import Decimal
from uuid import UUID

import click

from tests.data_generators import (
    CompanyGenerator,
    ConsumptionGenerator,
    CooperationGenerator,
    MemberGenerator,
    PlanGenerator,
    WorkerAffiliationGenerator,
)
from workers_control.core.injector import Injector
from workers_control.core.records import ProductionCosts
from workers_control.db import commit_changes


def create_generate_cli_group(injector: Injector) -> click.Group:
    generate = click.Group(
        name="generate",
        help="""
        Generate test data for the development database.

        Run `flask generate COMMAND --help` for more information on a specific command.
        """,
    )

    @generate.command("member")
    @click.option(
        "--name",
        "-n",
        help="Name of the member to be created.",
        type=str,
        default="Test Member",
        show_default=True,
    )
    @click.option(
        "--email",
        "-e",
        help="Email of the member to be created. If not given, a random email will be generated.",
        type=str,
    )
    @click.option(
        "--password",
        "-p",
        help="Password for the member.",
        type=str,
        default="password",
        show_default=True,
    )
    @commit_changes
    def generate_member(name: str, email: str | None, password: str) -> None:
        """Create a member."""
        data_generator = injector.get(MemberGenerator)
        member_id = data_generator.create_member(
            name=name,
            email=email if email else None,
            password=password,
        )
        click.echo(f"Member with ID {member_id} created.")

    @generate.command("plan")
    @click.option(
        "--name",
        "-n",
        help="Name of the plan to be created.",
        type=str,
        default="Test Plan",
        show_default=True,
    )
    @click.option(
        "--description",
        "-d",
        help="Description of the plan to be created.",
        type=str,
        default="This is a test plan.",
        show_default=True,
    )
    @click.option(
        "--production-unit",
        "-u",
        help="Description of the production unit.",
        type=str,
        default="1 Liter Bottle",
        show_default=True,
    )
    @click.option(
        "--planner",
        "-p",
        help="ID of the company who is the planner of the plan. If not given, a company will be created.",
        type=UUID,
    )
    @click.option(
        "--amount",
        "-a",
        help="Amount of the product to be produced.",
        type=int,
        default=100,
        show_default=True,
    )
    @click.option(
        "--labour-cost",
        "-lc",
        help="Labour cost.",
        type=Decimal,
        default=Decimal("1"),
        show_default=True,
    )
    @click.option(
        "--means-cost",
        "-mc",
        help="Fixed means cost.",
        type=Decimal,
        default=Decimal("1"),
        show_default=True,
    )
    @click.option(
        "--resource-cost",
        "-rc",
        help="Resource cost.",
        type=Decimal,
        default=Decimal("1"),
        show_default=True,
    )
    @click.option(
        "--timeframe",
        "-t",
        help="Timeframe of the plan in days.",
        type=int,
        default=14,
        show_default=True,
    )
    @click.option(
        "--public",
        "-pub",
        help="Whether the plan is a public plan.",
        is_flag=True,
        default=False,
        show_default=True,
    )
    @commit_changes
    def generate_plan(
        name: str,
        description: str,
        production_unit: str,
        labour_cost: Decimal,
        means_cost: Decimal,
        resource_cost: Decimal,
        planner: UUID | None,
        amount: int,
        timeframe: int,
        public: bool,
    ) -> None:
        """Create a plan."""
        costs = ProductionCosts(
            labour_cost=labour_cost,
            resource_cost=resource_cost,
            means_cost=means_cost,
        )
        data_generator = injector.get(PlanGenerator)
        plan_id = data_generator.create_plan(
            amount=amount,
            product_name=name,
            description=description,
            is_public_service=public,
            production_unit=production_unit,
            costs=costs,
            planner=planner if planner else None,
            timeframe=timeframe,
        )
        click.echo(f"Plan with ID {plan_id} created.")

    @generate.command("company")
    @click.option(
        "--name",
        "-n",
        help="Name of the company to be created.",
        type=str,
        default="Test Company",
        show_default=True,
    )
    @click.option(
        "--email",
        "-e",
        help="Email of the company to be created. If not given, a random email will be generated.",
        type=str,
    )
    @click.option(
        "--password",
        "-p",
        help="Password for the company.",
        type=str,
        default="password",
        show_default=True,
    )
    @click.option(
        "--worker",
        "-w",
        help="ID of the member to be added as a worker. Can be repeated to add multiple workers.",
        type=UUID,
        multiple=True,
    )
    @commit_changes
    def generate_company(
        name: str,
        email: str | None,
        password: str,
        worker: tuple[UUID],
    ) -> None:
        """Create a company."""
        data_generator = injector.get(CompanyGenerator)
        company_id = data_generator.create_company(
            name=name,
            email=email if email else None,
            password=password,
            workers=list(worker) if worker else None,
        )
        click.echo(f"Company with ID {company_id} created.")

    @generate.command("private-consumption")
    @click.option(
        "--plan",
        "-p",
        help="ID of plan to be consumed. If no plan is given, a plan will be created automatically.",
        type=UUID,
    )
    @commit_changes
    def generate_private_consumption(
        plan: UUID | None,
    ) -> None:
        """
        Create a private consumption.
        """
        data_generator = injector.get(ConsumptionGenerator)
        data_generator.create_private_consumption(
            plan=plan,
        )
        click.echo("Private consumption created.")

    @generate.command("productive-consumption-of-r")
    @click.option(
        "--plan",
        "-p",
        help="ID of plan to be consumed. If no plan is given, a plan will be created automatically.",
        type=UUID,
    )
    @commit_changes
    def generate_productive_consumption_of_r(plan: UUID | None) -> None:
        """
        Create a productive consumption of raw materials.
        """
        data_generator = injector.get(ConsumptionGenerator)
        data_generator.create_resource_consumption_by_company(
            plan=plan,
        )
        click.echo("Productive consumption created.")

    @generate.command("productive-consumption-of-p")
    @click.option(
        "--plan",
        "-p",
        help="ID of plan to be consumed. If no plan is given, a plan will be created automatically.",
        type=UUID,
    )
    @commit_changes
    def generate_productive_consumption_of_p(
        plan: UUID | None,
    ) -> None:
        """
        Create a productive consumption of fixed means.
        """
        data_generator = injector.get(ConsumptionGenerator)
        data_generator.create_fixed_means_consumption(
            plan=plan,
        )
        click.echo("Productive consumption created.")

    @generate.command("cooperation")
    @click.option(
        "--name",
        "-n",
        help="Name of the cooperation to be created.",
        type=str,
        default="Test Cooperation",
        show_default=True,
    )
    @click.option(
        "--coordinator",
        "-c",
        help="ID of the company who is the coordinator of the cooperation. If not given, a company will be created.",
        type=UUID,
    )
    @click.option(
        "--plans",
        "-p",
        help="ID of plan to be included in the cooperation. Can be repeated to include multiple plans.",
        multiple=True,
        type=UUID,
    )
    @commit_changes
    def generate_cooperation(
        name: str,
        coordinator: UUID | None,
        plans: tuple[UUID],
    ) -> None:
        """Create a cooperation."""
        data_generator = injector.get(CooperationGenerator)
        cooperation_id = data_generator.create_cooperation(
            name=name,
            plans=list(plans) if plans else None,
            coordinator=coordinator if coordinator else None,
        )
        click.echo(f"Cooperation with ID {cooperation_id} created.")

    @generate.command("worker-company-affiliation")
    @click.argument("company", type=UUID, nargs=1)
    @click.argument("worker", type=UUID, nargs=-1)
    @commit_changes
    def generate_company_worker_affiliation(
        company: UUID,
        worker: tuple[UUID],
    ) -> None:
        """Create a worker-company affiliation."""
        if not worker:
            click.echo("No workers provided. Please provide at least one worker ID.")
            return

        data_generator = injector.get(WorkerAffiliationGenerator)
        data_generator.add_workers_to_company(
            company=company,
            workers=list(worker),
        )

        click.echo(
            f"Worker(s) {', '.join(str(w) for w in worker)} added to company {company}."
        )

    return generate
