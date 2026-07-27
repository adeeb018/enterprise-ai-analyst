from abc import ABC, abstractmethod

from src.sql.models import ValidationIssue

from .context import ValidationContext


class ValidationRule(ABC):
    """
    Base class for every SQL validation rule.
    """

    @abstractmethod
    def validate(
        self,
        context: ValidationContext,
    ) -> list[ValidationIssue]:
        ...