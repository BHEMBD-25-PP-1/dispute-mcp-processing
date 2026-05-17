from pydantic import BaseModel


class DisputeRequest(BaseModel):
    text: str