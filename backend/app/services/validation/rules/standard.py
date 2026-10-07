import re
from dataclasses import dataclass

import pandas as pd

from app.domain.enums import ValidationSeverity
from app.services.validation.rules.base import (
    ValidationContext,
    ValidationResult,
    ValidationRule,
    build_result,
    nonblank,
)

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_PATTERN = re.compile(r"^\+?[\d\s().-]{7,25}$")


@dataclass(frozen=True)
class RequiredFieldRule(ValidationRule):
    field: str

    def validate(
        self, dataframe: pd.DataFrame, context: ValidationContext
    ) -> list[ValidationResult]:
        source = context.source_for(self.field)
        mask = (
            pd.Series(True, index=dataframe.index)
            if source is None or source not in dataframe
            else ~nonblank(dataframe[source])
        )
        result = build_result(
            dataframe=dataframe,
            mask=mask,
            context=context,
            rule="required_field",
            severity=ValidationSeverity.ERROR,
            field=self.field,
            message=f"Required field {self.field} is missing or blank",
        )
        return [result] if result else []


@dataclass(frozen=True)
class EmailFormatRule(ValidationRule):
    field: str = "email"

    def validate(
        self, dataframe: pd.DataFrame, context: ValidationContext
    ) -> list[ValidationResult]:
        source = context.source_for(self.field)
        if source is None or source not in dataframe:
            return []
        present = nonblank(dataframe[source])
        mask = present & ~dataframe[source].astype(str).str.fullmatch(EMAIL_PATTERN)
        result = build_result(
            dataframe=dataframe,
            mask=mask,
            context=context,
            rule="email_format",
            severity=ValidationSeverity.WARNING,
            field=self.field,
            message=f"{self.field} contains invalid email addresses",
        )
        return [result] if result else []


@dataclass(frozen=True)
class PhoneFormatRule(ValidationRule):
    field: str = "phone"

    def validate(
        self, dataframe: pd.DataFrame, context: ValidationContext
    ) -> list[ValidationResult]:
        source = context.source_for(self.field)
        if source is None or source not in dataframe:
            return []
        values = dataframe[source].astype(str)
        digit_count = values.str.replace(r"\D", "", regex=True).str.len()
        present = nonblank(dataframe[source])
        mask = present & (
            ~values.str.fullmatch(PHONE_PATTERN) | ~digit_count.between(7, 15)
        )
        result = build_result(
            dataframe=dataframe,
            mask=mask,
            context=context,
            rule="phone_format",
            severity=ValidationSeverity.WARNING,
            field=self.field,
            message=f"{self.field} contains invalid phone numbers",
        )
        return [result] if result else []


@dataclass(frozen=True)
class DateParseRule(ValidationRule):
    field: str

    def validate(
        self, dataframe: pd.DataFrame, context: ValidationContext
    ) -> list[ValidationResult]:
        source = context.source_for(self.field)
        if source is None or source not in dataframe:
            return []
        present = nonblank(dataframe[source])
        parsed = pd.to_datetime(dataframe[source], errors="coerce", format="mixed")
        result = build_result(
            dataframe=dataframe,
            mask=present & parsed.isna(),
            context=context,
            rule="date_parse",
            severity=ValidationSeverity.WARNING,
            field=self.field,
            message=f"{self.field} contains values that cannot be parsed as dates",
        )
        return [result] if result else []


class DuplicateRule(ValidationRule):
    def validate(
        self, dataframe: pd.DataFrame, context: ValidationContext
    ) -> list[ValidationResult]:
        result = build_result(
            dataframe=dataframe,
            mask=dataframe.duplicated(keep=False),
            context=context,
            rule="duplicate_row",
            severity=ValidationSeverity.WARNING,
            field=None,
            message="Dataset contains duplicate rows",
        )
        return [result] if result else []


@dataclass(frozen=True)
class UniqueFieldRule(ValidationRule):
    field: str

    def validate(
        self, dataframe: pd.DataFrame, context: ValidationContext
    ) -> list[ValidationResult]:
        source = context.source_for(self.field)
        if source is None or source not in dataframe:
            return []
        present = nonblank(dataframe[source])
        result = build_result(
            dataframe=dataframe,
            mask=present & dataframe[source].duplicated(keep=False),
            context=context,
            rule="unique_field",
            severity=ValidationSeverity.ERROR,
            field=self.field,
            message=f"{self.field} must contain unique values",
        )
        return [result] if result else []


@dataclass(frozen=True)
class TypeRule(ValidationRule):
    field: str
    expected_type: str

    def validate(
        self, dataframe: pd.DataFrame, context: ValidationContext
    ) -> list[ValidationResult]:
        source = context.source_for(self.field)
        if source is None or source not in dataframe or self.expected_type == "string":
            return []
        series = dataframe[source]
        present = nonblank(series)
        if self.expected_type in {"number", "integer"}:
            converted = pd.to_numeric(series, errors="coerce")
            invalid = converted.isna()
            if self.expected_type == "integer":
                invalid |= converted.notna() & converted.mod(1).ne(0)
        elif self.expected_type == "boolean":
            invalid = ~series.astype(str).str.lower().isin(
                {"true", "false", "1", "0", "yes", "no"}
            )
        elif self.expected_type == "datetime":
            invalid = pd.to_datetime(series, errors="coerce", format="mixed").isna()
        else:
            return []
        result = build_result(
            dataframe=dataframe,
            mask=present & invalid,
            context=context,
            rule="type",
            severity=ValidationSeverity.WARNING,
            field=self.field,
            message=f"{self.field} must contain {self.expected_type} values",
        )
        return [result] if result else []


@dataclass(frozen=True)
class RangeRule(ValidationRule):
    field: str
    minimum: float | None = None
    maximum: float | None = None

    def validate(
        self, dataframe: pd.DataFrame, context: ValidationContext
    ) -> list[ValidationResult]:
        source = context.source_for(self.field)
        if source is None or source not in dataframe:
            return []
        converted = pd.to_numeric(dataframe[source], errors="coerce")
        mask = pd.Series(False, index=dataframe.index)
        if self.minimum is not None:
            mask |= converted < self.minimum
        if self.maximum is not None:
            mask |= converted > self.maximum
        result = build_result(
            dataframe=dataframe,
            mask=mask,
            context=context,
            rule="range",
            severity=ValidationSeverity.WARNING,
            field=self.field,
            message=f"{self.field} contains values outside the allowed range",
        )
        return [result] if result else []


class UnknownColumnRule(ValidationRule):
    def validate(
        self, dataframe: pd.DataFrame, context: ValidationContext
    ) -> list[ValidationResult]:
        results: list[ValidationResult] = []
        all_rows = frozenset(range(len(dataframe.index)))
        for column in context.unknown_columns:
            results.append(
                ValidationResult(
                    rule="unknown_column",
                    severity=ValidationSeverity.INFO,
                    field=column,
                    message=f"Column {column} is not mapped to the canonical schema",
                    affected_rows=all_rows,
                )
            )
        return results
