from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import TypeAlias, TypeVar
from uuid import UUID

from workers_control.web.translator import Translator

T = TypeVar("T")
ValidatorResult: TypeAlias = T | list[str]


@dataclass
class RegisterPrivateConsumptionOfBasicServiceFormValidator:
    translator: Translator

    def validate_basic_service_id_string(self, text: str) -> ValidatorResult[UUID]:
        if text:
            try:
                return UUID(text)
            except ValueError:
                return [self.translator.gettext("Basic service ID is invalid.")]
        else:
            return [self.translator.gettext("Basic service ID is invalid.")]

    def validate_amount_string(self, text: str) -> ValidatorResult[Decimal]:
        if not text:
            return [self.translator.gettext("You must specify an amount.")]
        try:
            amount = Decimal(text)
        except InvalidOperation:
            return [self.translator.gettext("This is not a valid number.")]
        if amount <= 0:
            return [self.translator.gettext("Must be a number larger than zero.")]
        return amount
