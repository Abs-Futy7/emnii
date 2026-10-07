import pytest

from app.services.schema_mapping import (
    DeterministicMappingEngine,
    normalize_source_name,
)


@pytest.mark.parametrize(
    ("source", "normalized"),
    [
        ("Customer Name", "customer_name"),
        ("E-Mail", "e_mail"),
        ("MOB NO", "mob_no"),
    ],
)
def test_source_name_normalization(source: str, normalized: str) -> None:
    assert normalize_source_name(source) == normalized


@pytest.mark.parametrize(
    ("source", "target"),
    [
        ("cust_nm", "customer_name"),
        ("mob_no", "phone"),
        ("email_address", "email"),
        ("created_date", "created_at"),
    ],
)
def test_known_messy_columns_map_deterministically(source: str, target: str) -> None:
    suggestion = DeterministicMappingEngine().suggest(source, [])

    assert suggestion.target_field == target
    assert suggestion.confidence == 0.94
    assert suggestion.method == "alias"


def test_ambiguous_code_column_remains_unresolved() -> None:
    suggestion = DeterministicMappingEngine().suggest("code", ["A1", "B2"])

    assert suggestion.target_field is None
    assert suggestion.confidence < 0.72
    assert suggestion.method == "unresolved"


def test_value_evidence_improves_but_does_not_fake_certainty() -> None:
    engine = DeterministicMappingEngine()

    lexical_only = engine.suggest("email_value", [])
    with_values = engine.suggest("email_value", ["one@example.com", "two@example.com"])

    assert with_values.target_field == "email"
    assert with_values.confidence > lexical_only.confidence
    assert with_values.confidence < 1
    assert with_values.method.endswith("+values")
