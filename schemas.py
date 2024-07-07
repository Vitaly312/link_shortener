from pydantic import BaseModel


class LinkInModel(BaseModel):
    original_link: str

class LinkOutModel(BaseModel):
    short_link: str
    access_key: str

    class Config:
        from_attributes = True

class LinkStatistics(BaseModel):
    original_link: str
    short_link: str
    number_of_transitions: int
    number_of_transitions_by_country: dict[str, int]
    number_of_transitions_from_sites: int