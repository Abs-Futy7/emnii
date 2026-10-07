import ipaddress
import re
from dataclasses import dataclass

import pandas as pd

from app.domain.enums import PIIType
from app.utils.redaction import mask_pii_sample

EMAIL_PATTERN = re.compile(r"(?<![\w.+-])([\w.+-]+@[\w-]+(?:\.[\w-]+)+)(?![\w.-])")
IPV4_PATTERN = re.compile(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)")
IPV6_PATTERN = re.compile(
    r"(?<![0-9A-Fa-f:])(?:[0-9A-Fa-f]{0,4}:){2,7}[0-9A-Fa-f]{0,4}"
    r"(?![0-9A-Fa-f:])"
)
CARD_PATTERN = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")
PHONE_PATTERN = re.compile(r"(?<!\w)\+?\d[\d\s().-]{5,}\d(?!\w)")


@dataclass(frozen=True)
class DetectedPIIFinding:
    column_name: str
    pii_type: PIIType
    count: int
    confidence: float
    method: str
    sample_redacted_values: tuple[str, ...]


class PIIScanner:
    MAX_SAMPLES = 5

    def scan(
        self,
        dataframe: pd.DataFrame,
        schema_pii: dict[str, PIIType] | None = None,
    ) -> list[DetectedPIIFinding]:
        schema_pii = schema_pii or {}
        findings: list[DetectedPIIFinding] = []
        for raw_column in dataframe.columns:
            column = str(raw_column)
            values = [
                str(value).strip()
                for value in dataframe[raw_column].dropna().tolist()
                if str(value).strip()
            ]
            schema_type = schema_pii.get(column)
            if schema_type is not None and values:
                findings.append(
                    self._finding(
                        column,
                        schema_type,
                        values,
                        confidence=0.99,
                        method="schema_context",
                    )
                )

            findings.extend(self._pattern_findings(column, values))
        return findings

    def _pattern_findings(
        self, column: str, values: list[str]
    ) -> list[DetectedPIIFinding]:
        matches: dict[PIIType, list[str]] = {
            PIIType.EMAIL: [],
            PIIType.PHONE: [],
            PIIType.IP_ADDRESS: [],
            PIIType.CREDIT_CARD: [],
        }
        for value in values:
            matches[PIIType.EMAIL].extend(
                match.group(1) for match in EMAIL_PATTERN.finditer(value)
            )
            matches[PIIType.IP_ADDRESS].extend(self._ip_matches(value))
            cards = [
                match.group(0).strip()
                for match in CARD_PATTERN.finditer(value)
                if self._passes_luhn(match.group(0))
            ]
            matches[PIIType.CREDIT_CARD].extend(cards)
            matches[PIIType.PHONE].extend(
                candidate
                for candidate in (
                    match.group(0).strip() for match in PHONE_PATTERN.finditer(value)
                )
                if self._is_phone(candidate)
            )

        configuration = {
            PIIType.EMAIL: (0.99, "regex"),
            PIIType.PHONE: (0.90, "regex"),
            PIIType.IP_ADDRESS: (1.0, "validated_pattern"),
            PIIType.CREDIT_CARD: (1.0, "regex+luhn"),
        }
        return [
            self._finding(
                column,
                pii_type,
                detected,
                confidence=configuration[pii_type][0],
                method=configuration[pii_type][1],
            )
            for pii_type, detected in matches.items()
            if detected
        ]

    def _finding(
        self,
        column: str,
        pii_type: PIIType,
        matches: list[str],
        *,
        confidence: float,
        method: str,
    ) -> DetectedPIIFinding:
        masked = list(
            dict.fromkeys(mask_pii_sample(value, pii_type) for value in matches)
        )
        return DetectedPIIFinding(
            column_name=column,
            pii_type=pii_type,
            count=len(matches),
            confidence=confidence,
            method=method,
            sample_redacted_values=tuple(masked[: self.MAX_SAMPLES]),
        )

    @staticmethod
    def _ip_matches(value: str) -> list[str]:
        candidates = [match.group(0) for match in IPV4_PATTERN.finditer(value)]
        candidates.extend(match.group(0) for match in IPV6_PATTERN.finditer(value))
        valid: list[str] = []
        for candidate in candidates:
            try:
                ipaddress.ip_address(candidate)
            except ValueError:
                continue
            valid.append(candidate)
        return valid

    @classmethod
    def _is_phone(cls, value: str) -> bool:
        digits = re.sub(r"\D", "", value)
        if not 7 <= len(digits) <= 15:
            return False
        try:
            ipaddress.ip_address(value)
        except ValueError:
            pass
        else:
            return False
        return not (len(digits) >= 13 and cls._passes_luhn(value))

    @staticmethod
    def _passes_luhn(value: str) -> bool:
        digits = [int(character) for character in value if character.isdigit()]
        if not 13 <= len(digits) <= 19 or len(set(digits)) == 1:
            return False
        checksum = 0
        parity = len(digits) % 2
        for index, digit in enumerate(digits):
            if index % 2 == parity:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit
        return checksum % 10 == 0
