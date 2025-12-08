# Task 4: Validate and normalize messy JSON input
# Given this incoming JSON:
# {
#     "user": {"id": "123", "age": "37"},
#     "emails": "anton@example.com,   a@example.com ,",
#     "admin": "yes"
# }
#
# Task:
# Write a function:
# def normalize_payload(payload: dict) -> NormalizedUser:
#     ...
# Where NormalizedUser is a dataclass:
# 	•	id: int
# 	•	age: int | None (age may be missing or invalid → set to None)
# 	•	emails: list[str] (dedupe + trim + filter empty)
# 	•	admin: bool (“yes”/“no”/“1”/“0” → bool)
# 	•	Invalid fields → ignore with a log message

# What this tests
# 	•	Data validation
# 	•	Clean conversion logic
# 	•	Use of dataclasses / type hints
# 	•	Robust input handling

import json
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator, AliasPath, ConfigDict


class NormalizedUser(BaseModel):
    id: int = Field(validation_alias=AliasPath("user", "id"))
    age: Optional[int] = Field(default=None, validation_alias=AliasPath("user", "age"))
    emails: list[str]
    is_admin: bool = Field(default=False, validation_alias="admin")

    model_config = ConfigDict(extra="allow")

    @field_validator("emails", mode="before")
    @classmethod
    def validate_emails(cls, v):
        if isinstance(v, str):
            s = str(v)
            ems = [em.strip() for em in s.split(",") if em.strip()]
            return ems
        elif isinstance(v, list):
            return [em.strip() for em in v if em.strip()]
        else:
            raise ValueError("emails must be a string of emails, separated by comma")

    @field_validator("is_admin", mode="before")
    @classmethod
    def validate_is_admin_bool(cls, v: Any):
        if isinstance(v, bool):
            return v
        elif isinstance(v, int):
            return bool(v)
        elif isinstance(v, str):
            if v.lower() in {"1", "yes", "true"}:
                return True
            elif v.lower() in {"0", "no", "false"}:
                return False
            else:
                raise ValueError("invalid bool string")
        else:
            raise ValueError("field must be bool|int|str")


def normalize_payload(payload: dict) -> NormalizedUser:
    user = NormalizedUser.model_validate(payload)

    if user.__pydantic_extra__:
        for k, v in user.__pydantic_extra__.items():
            print(f"ignored extra attribute from input: {k} => {v!r}")

    user.__delattr__("__pydantic_extra__")

    return user


def validate_json(json_str: str):
    print(f"validating json:\n{json_str}\n------")
    try:
        payload = json.loads(json_str)
        user = normalize_payload(payload)
        print(user)
    except Exception as e:
        print(f"validation error: {e}")
    finally:
        print("--- done ---")
        print()


def main():
    validate_json(
        r"""{ "user": {"id": "123", "age": "37"}, "emails": "anton@example.com,   a@example.com ,", "admin": "yes" }"""
    )
    validate_json(
        r"""{ "user": {"id": "123", "age": "37"}, "emails": "anton@example.com,   a@example.com ,", "admin": "0" }"""
    )
    validate_json(
        r"""{ "user": {"id": "123", "age": "37"}, "emails": "anton@example.com,   a@example.com ,", "admin": "0", "ex\\tra": "'" }"""
    )

    validate_json(r"""{ "user": {"id": "123", "age": "37"}, "emails": 600, "admin": "yes" }""")
    validate_json(
        r"""{ "user": {"id": "123", "age": "37"}, "emails": ["a@a.com", "", "b@ninja.ae"], "admin": "1" }"""
    )


if __name__ == "__main__":
    main()
