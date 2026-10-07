import pandas as pd
import pytest

from app.services.validation.rules import (
    DateParseRule,
    DuplicateRule,
    EmailFormatRule,
    PhoneFormatRule,
    RangeRule,
    RequiredFieldRule,
    TypeRule,
    UniqueFieldRule,
    UnknownColumnRule,
    ValidationContext,
)


def result_count(rule: object, frame: pd.DataFrame, context: ValidationContext) -> int:
    results = rule.validate(frame, context)  # type: ignore[attr-defined]
    assert len(results) == 1
    return results[0].affected_count


@pytest.fixture
def validation_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": ["1", "2", "2"],
            "mail": ["good@example.com", "not-an-email", None],
            "mobile": ["+1 202 555 0100", "12", None],
            "joined": ["2025-01-01", "not-a-date", None],
            "age": [20, -1, 20],
            "quantity": ["1", "2.5", "bad"],
            "required": ["yes", "", None],
        }
    )


@pytest.fixture
def validation_context() -> ValidationContext:
    return ValidationContext(
        field_sources={
            "customer_id": "id",
            "email": "mail",
            "phone": "mobile",
            "created_at": "joined",
            "age": "age",
            "quantity": "quantity",
            "required_field": "required",
        },
        unknown_columns=("legacy_code",),
        max_examples=2,
    )


def test_required_field_rule(
    validation_frame: pd.DataFrame, validation_context: ValidationContext
) -> None:
    assert (
        result_count(
            RequiredFieldRule("required_field"), validation_frame, validation_context
        )
        == 2
    )


def test_email_format_rule(
    validation_frame: pd.DataFrame, validation_context: ValidationContext
) -> None:
    assert result_count(EmailFormatRule(), validation_frame, validation_context) == 1


def test_phone_format_rule(
    validation_frame: pd.DataFrame, validation_context: ValidationContext
) -> None:
    assert result_count(PhoneFormatRule(), validation_frame, validation_context) == 1


def test_date_parse_rule(
    validation_frame: pd.DataFrame, validation_context: ValidationContext
) -> None:
    assert (
        result_count(DateParseRule("created_at"), validation_frame, validation_context)
        == 1
    )


def test_duplicate_rule() -> None:
    frame = pd.DataFrame({"id": [1, 1, 2], "name": ["A", "A", "B"]})
    assert result_count(DuplicateRule(), frame, ValidationContext({})) == 2


def test_unique_field_rule(
    validation_frame: pd.DataFrame, validation_context: ValidationContext
) -> None:
    assert (
        result_count(
            UniqueFieldRule("customer_id"), validation_frame, validation_context
        )
        == 2
    )


def test_type_rule(
    validation_frame: pd.DataFrame, validation_context: ValidationContext
) -> None:
    assert (
        result_count(
            TypeRule("quantity", "integer"), validation_frame, validation_context
        )
        == 2
    )


def test_range_rule(
    validation_frame: pd.DataFrame, validation_context: ValidationContext
) -> None:
    assert (
        result_count(
            RangeRule("age", minimum=0, maximum=120),
            validation_frame,
            validation_context,
        )
        == 1
    )


def test_unknown_column_rule(
    validation_frame: pd.DataFrame, validation_context: ValidationContext
) -> None:
    result = UnknownColumnRule().validate(validation_frame, validation_context)[0]

    assert result.field == "legacy_code"
    assert result.affected_count == len(validation_frame)
