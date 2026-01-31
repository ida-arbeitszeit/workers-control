"""
Definition of database tables.
"""

from datetime import UTC, datetime
from decimal import Decimal
from sqlite3 import Connection as SQLiteConnection
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Column,
    DateTime,
    Dialect,
    Engine,
    ForeignKey,
    String,
    Table,
    Text,
    TypeDecorator,
    Uuid,
    event,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.pool import ConnectionPoolEntry

from workers_control.core.transfers import TransferType
from workers_control.db.db import Base


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(
    dbapi_connection: Any, connection_record: ConnectionPoolEntry
) -> None:
    # This event listener is necessary to enable "on delete cascading" in SQlite
    # https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#sqlite-foreign-keys
    # https://docs.sqlalchemy.org/en/20/orm/cascades.html#using-foreign-key-on-delete-cascade-with-orm-relationships
    if type(dbapi_connection) is SQLiteConnection:
        ac = dbapi_connection.autocommit
        dbapi_connection.autocommit = True

        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

        # restore orginal autocommit setting
        dbapi_connection.autocommit = ac


class TZDateTime(TypeDecorator):
    """
    We store all datetimes in UTC without timezone info, but require
    that all datetimes passed in have tzinfo set.
    Output datetimes have tzinfo set to UTC.
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(
        self, value: datetime | None, dialect: Dialect
    ) -> datetime | None:
        if value is not None:
            if not value.tzinfo or value.tzinfo.utcoffset(value) is None:
                raise TypeError("tzinfo is required")
            value = value.astimezone(UTC).replace(tzinfo=None)
        return value

    def process_result_value(
        self, value: datetime | None, dialect: Dialect
    ) -> datetime | None:
        if value is not None:
            value = value.replace(tzinfo=UTC)
        return value


class User(Base):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    password: Mapped[str] = mapped_column(String(300))
    email_address: Mapped[str] = mapped_column(ForeignKey("email.address"), unique=True)

    def __str__(self) -> str:
        return f"User {self.email_address} ({self.id})"


class Email(Base):
    __tablename__ = "email"

    address: Mapped[str] = mapped_column(primary_key=True)
    confirmed_on: Mapped[datetime | None] = mapped_column(TZDateTime)


class SocialAccounting(Base):
    __tablename__ = "social_accounting"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    account_psf: Mapped[UUID] = mapped_column(Uuid, ForeignKey("account.id"))


# Association table Company - Member
jobs_table = Table(
    "jobs",
    Base.metadata,
    Column("member_id", Uuid, ForeignKey("member.id"), primary_key=True),
    Column("company_id", Uuid, ForeignKey("company.id"), primary_key=True),
)


class Member(Base):
    __tablename__ = "member"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("user.id"), unique=True)
    name: Mapped[str] = mapped_column(String(1000))
    registered_on: Mapped[datetime] = mapped_column(TZDateTime)
    account: Mapped[UUID] = mapped_column(Uuid, ForeignKey("account.id"))

    workplaces = relationship(
        "Company",
        secondary=jobs_table,
        back_populates="workers",
    )


class Company(Base):
    __tablename__ = "company"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("user.id"), unique=True)
    name: Mapped[str] = mapped_column(String(1000))
    registered_on: Mapped[datetime] = mapped_column(TZDateTime)
    p_account: Mapped[UUID] = mapped_column(Uuid, ForeignKey("account.id"))
    r_account: Mapped[UUID] = mapped_column(Uuid, ForeignKey("account.id"))
    a_account: Mapped[UUID] = mapped_column(Uuid, ForeignKey("account.id"))
    prd_account: Mapped[UUID] = mapped_column(Uuid, ForeignKey("account.id"))

    def __repr__(self):
        return "<Company(name='%s')>" % (self.name,)

    workers = relationship(
        "Member",
        secondary=jobs_table,
        back_populates="workplaces",
    )


class Accountant(Base):
    __tablename__ = "accountant"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("user.id"), unique=True)
    name: Mapped[str] = mapped_column(String(1000))


class PlanDraft(Base):
    __tablename__ = "plan_draft"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    plan_creation_date: Mapped[datetime] = mapped_column(TZDateTime)
    planner: Mapped[UUID] = mapped_column(Uuid, ForeignKey("company.id"))
    costs_p: Mapped[Decimal]
    costs_r: Mapped[Decimal]
    costs_a: Mapped[Decimal]
    prd_name: Mapped[str] = mapped_column(String(100))
    prd_unit: Mapped[str] = mapped_column(String(100))
    prd_amount: Mapped[int]
    description: Mapped[str] = mapped_column(String(5000))
    timeframe: Mapped[Decimal]
    is_public_service: Mapped[bool] = mapped_column(default=False)


class Plan(Base):
    __tablename__ = "plan"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    plan_creation_date: Mapped[datetime] = mapped_column(TZDateTime)
    planner: Mapped[UUID] = mapped_column(Uuid, ForeignKey("company.id"))
    costs_p: Mapped[Decimal]
    costs_r: Mapped[Decimal]
    costs_a: Mapped[Decimal]
    prd_name: Mapped[str] = mapped_column(String(100))
    prd_unit: Mapped[str] = mapped_column(String(100))
    prd_amount: Mapped[int]
    description: Mapped[str] = mapped_column(String(5000))
    timeframe: Mapped[Decimal]
    is_public_service: Mapped[bool] = mapped_column(default=False)
    requested_cooperation: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("cooperation.id")
    )
    hidden_by_user: Mapped[bool] = mapped_column(default=False)

    review: Mapped["PlanReview  | None"] = relationship(
        "PlanReview", back_populates="plan"
    )
    approval: Mapped["PlanApproval | None"] = relationship(
        "PlanApproval", back_populates="plan"
    )


class PlanCooperation(Base):
    __tablename__ = "plan_cooperation"

    plan: Mapped[UUID] = mapped_column(Uuid, ForeignKey("plan.id"), primary_key=True)
    cooperation: Mapped[UUID] = mapped_column(Uuid, ForeignKey("cooperation.id"))


class PlanReview(Base):
    __tablename__ = "plan_review"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    rejection_date: Mapped[datetime | None] = mapped_column(TZDateTime)
    plan_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("plan.id", ondelete="CASCADE")
    )

    plan: Mapped["Plan"] = relationship("Plan", back_populates="review")

    def __repr__(self) -> str:
        return f"PlanReview(id={self.id!r}, plan_id={self.plan_id!r}, rejection_date={self.rejection_date!r})"


class PlanApproval(Base):
    __tablename__ = "plan_approval"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    plan_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("plan.id", ondelete="CASCADE")
    )
    date: Mapped[datetime] = mapped_column(TZDateTime)
    transfer_of_credit_p: Mapped[UUID] = mapped_column(Uuid, ForeignKey("transfer.id"))
    transfer_of_credit_r: Mapped[UUID] = mapped_column(Uuid, ForeignKey("transfer.id"))
    transfer_of_credit_a: Mapped[UUID] = mapped_column(Uuid, ForeignKey("transfer.id"))

    plan: Mapped["Plan"] = relationship("Plan", back_populates="approval")


class Account(Base):
    __tablename__ = "account"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)


class Transfer(Base):
    __tablename__ = "transfer"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    date: Mapped[datetime] = mapped_column(TZDateTime, index=True)
    debit_account: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("account.id"), index=True
    )
    credit_account: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("account.id"), index=True
    )
    value: Mapped[Decimal]
    type: Mapped[TransferType]

    def __repr__(self) -> str:
        fields = ", ".join(
            [
                f"id={self.id!r}",
                f"date={self.date!r}",
                f"debit_account={self.debit_account!r}",
                f"credit_account={self.credit_account!r}",
                f"value={self.value!r}",
                f"type={self.type!r}",
            ]
        )
        return f"Transfer({fields})"


class PrivateConsumption(Base):
    __tablename__ = "private_consumption"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    plan_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("plan.id"))
    transfer_of_private_consumption: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("transfer.id")
    )
    transfer_of_compensation: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("transfer.id")
    )
    amount: Mapped[int]


class ProductiveConsumption(Base):
    __tablename__ = "productive_consumption"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    plan_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("plan.id"))
    transfer_of_productive_consumption: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("transfer.id")
    )
    transfer_of_compensation: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("transfer.id")
    )
    amount: Mapped[int]


class RegisteredHoursWorked(Base):
    __tablename__ = "registered_hours_worked"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    company: Mapped[UUID] = mapped_column(Uuid, ForeignKey("company.id"))
    worker: Mapped[UUID] = mapped_column(Uuid, ForeignKey("member.id"))
    transfer_of_work_certificates: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("transfer.id")
    )
    transfer_of_taxes: Mapped[UUID] = mapped_column(Uuid, ForeignKey("transfer.id"))
    registered_on: Mapped[datetime] = mapped_column(TZDateTime)


class CompanyWorkInvite(Base):
    __tablename__ = "company_work_invite"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    company: Mapped[UUID] = mapped_column(Uuid, ForeignKey("company.id"))
    member: Mapped[UUID] = mapped_column(Uuid, ForeignKey("member.id"))


class Cooperation(Base):
    __tablename__ = "cooperation"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    creation_date: Mapped[datetime] = mapped_column(TZDateTime)
    name: Mapped[str] = mapped_column(String(100))
    definition: Mapped[str] = mapped_column(String(5000))
    account: Mapped[UUID] = mapped_column(Uuid, ForeignKey("account.id"))


class CoordinationTenure(Base):
    __tablename__ = "coordination_tenure"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    company: Mapped[UUID] = mapped_column(Uuid, ForeignKey("company.id"))
    cooperation: Mapped[UUID] = mapped_column(Uuid, ForeignKey("cooperation.id"))
    start_date: Mapped[datetime] = mapped_column(TZDateTime)


class CoordinationTransferRequest(Base):
    __tablename__ = "coordination_transfer_request"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    requesting_coordination_tenure: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("coordination_tenure.id")
    )
    candidate: Mapped[UUID] = mapped_column(Uuid, ForeignKey("company.id"))
    request_date: Mapped[datetime] = mapped_column(TZDateTime)


class PasswordResetRequest(Base):
    __tablename__ = "password_reset_request"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    email_address: Mapped[str] = mapped_column(
        ForeignKey("email.address"), unique=False
    )
    reset_token: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(TZDateTime)


class EmailOutbox(Base):
    __tablename__ = "email_outbox"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(TZDateTime)
    recipient: Mapped[str] = mapped_column(String(1000))
    sender: Mapped[str] = mapped_column(String(1000))
    subject: Mapped[str] = mapped_column(String(1000))
    html: Mapped[str] = mapped_column(Text)
