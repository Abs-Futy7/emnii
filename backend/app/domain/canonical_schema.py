from dataclasses import dataclass


@dataclass(frozen=True)
class CanonicalFieldDefinition:
    name: str
    data_type: str
    aliases: tuple[str, ...] = ()
    description: str = ""


CANONICAL_FIELDS = (
    CanonicalFieldDefinition(
        "customer_id", "string", ("cust_id", "client_id", "customer_number")
    ),
    CanonicalFieldDefinition(
        "customer_name",
        "string",
        (
            "cust_name",
            "cust_nm",
            "customer",
            "client_name",
            "fullname",
            "full_name",
        ),
    ),
    CanonicalFieldDefinition("first_name", "string", ("firstname", "given_name")),
    CanonicalFieldDefinition("last_name", "string", ("lastname", "surname")),
    CanonicalFieldDefinition(
        "email", "email", ("mail", "e_mail", "email_address", "mail_address")
    ),
    CanonicalFieldDefinition(
        "phone",
        "phone",
        ("mobile", "mobile_no", "mob_no", "contact_no", "phone_no"),
    ),
    CanonicalFieldDefinition("address", "string", ("street_address", "addr")),
    CanonicalFieldDefinition("city", "string", ("town",)),
    CanonicalFieldDefinition("country", "string", ("nation", "country_name")),
    CanonicalFieldDefinition(
        "created_at",
        "datetime",
        ("created_date", "creation_date", "created_on", "join_date", "join_dt"),
    ),
    CanonicalFieldDefinition("order_id", "string", ("order_no", "order_number")),
    CanonicalFieldDefinition("ticket_id", "string", ("ticket_no", "case_id")),
    CanonicalFieldDefinition(
        "ticket_status", "string", ("case_status", "support_status")
    ),
)

CANONICAL_FIELD_BY_NAME = {field.name: field for field in CANONICAL_FIELDS}
