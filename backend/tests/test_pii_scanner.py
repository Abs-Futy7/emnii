import pandas as pd

from app.domain.enums import PIIType
from app.services.pii.scanner import PIIScanner
from app.utils.redaction import mask_pii_sample, redact_value


def test_redaction_utility_uses_stable_category_markers() -> None:
    assert redact_value("John Doe", PIIType.PERSON_NAME) == "[PERSON]"
    assert redact_value("john@example.com", PIIType.EMAIL) == "[EMAIL]"
    assert redact_value("01712345678", PIIType.PHONE) == "[PHONE]"


def test_display_samples_are_masked() -> None:
    assert mask_pii_sample("john@example.com", PIIType.EMAIL) == "j***@example.com"
    assert mask_pii_sample("01712345678", PIIType.PHONE) == "017****5678"
    assert (
        mask_pii_sample("4111 1111 1111 1111", PIIType.CREDIT_CARD)
        == "**** **** **** 1111"
    )


def test_scanner_detects_patterns_and_schema_context_without_raw_samples() -> None:
    frame = pd.DataFrame(
        {
            "full_name": ["John Doe"],
            "street": ["10 Main Street"],
            "contact": ["john@example.com"],
            "mobile": ["01712345678"],
            "source_ip": ["192.168.1.10"],
            "payment": ["4111 1111 1111 1111"],
            "invalid_card": ["4111 1111 1111 1112"],
        }
    )

    findings = PIIScanner().scan(
        frame,
        {
            "full_name": PIIType.PERSON_NAME,
            "street": PIIType.ADDRESS,
        },
    )
    by_type = {(finding.column_name, finding.pii_type): finding for finding in findings}

    assert by_type[("full_name", PIIType.PERSON_NAME)].method == "schema_context"
    assert by_type[("street", PIIType.ADDRESS)].method == "schema_context"
    assert by_type[("contact", PIIType.EMAIL)].count == 1
    assert by_type[("mobile", PIIType.PHONE)].count == 1
    assert by_type[("source_ip", PIIType.IP_ADDRESS)].count == 1
    assert by_type[("payment", PIIType.CREDIT_CARD)].method == "regex+luhn"
    assert ("invalid_card", PIIType.CREDIT_CARD) not in by_type

    serialized_samples = " ".join(
        sample for finding in findings for sample in finding.sample_redacted_values
    )
    for raw_value in (
        "John Doe",
        "10 Main Street",
        "john@example.com",
        "01712345678",
        "192.168.1.10",
        "4111 1111 1111 1111",
    ):
        assert raw_value not in serialized_samples
