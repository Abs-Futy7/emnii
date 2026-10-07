import re

from app.domain.enums import PIIType


def mask_pii_sample(value: str, pii_type: PIIType) -> str:
    """Return a display-safe sample that cannot reveal the original value."""
    stripped = value.strip()
    if pii_type == PIIType.EMAIL:
        local, separator, domain = stripped.partition("@")
        if separator and domain:
            return f"{local[:1]}***@{domain}"
        return "[EMAIL]"
    if pii_type == PIIType.PHONE:
        digits = re.sub(r"\D", "", stripped)
        if len(digits) >= 8:
            return f"{digits[:3]}****{digits[-4:]}"
        return "[PHONE]"
    if pii_type == PIIType.CREDIT_CARD:
        digits = re.sub(r"\D", "", stripped)
        return f"**** **** **** {digits[-4:]}" if len(digits) >= 4 else "[CREDIT_CARD]"
    if pii_type == PIIType.IP_ADDRESS:
        return "[IP_ADDRESS]"
    if pii_type == PIIType.PERSON_NAME:
        return "[PERSON]"
    if pii_type == PIIType.ADDRESS:
        return "[ADDRESS]"
    return "[REDACTED]"


def redact_value(value: str, pii_type: PIIType) -> str:
    """Replace a known PII value with a stable category marker."""
    del value
    markers = {
        PIIType.EMAIL: "[EMAIL]",
        PIIType.PHONE: "[PHONE]",
        PIIType.IP_ADDRESS: "[IP_ADDRESS]",
        PIIType.CREDIT_CARD: "[CREDIT_CARD]",
        PIIType.PERSON_NAME: "[PERSON]",
        PIIType.ADDRESS: "[ADDRESS]",
    }
    return markers[pii_type]
