from pydantic import BaseModel, field_validator


class EnrichRequest(BaseModel):
    address: str

    @field_validator("address")
    @classmethod
    def address_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("address must not be empty")
        return v
