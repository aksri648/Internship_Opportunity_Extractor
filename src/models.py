from pydantic import BaseModel


class Opportunity(BaseModel):
    job_title: str
    company: str
    eligible_batches: list[str]
    application_link: str
    confidence: str


class ExtractionResult(BaseModel):
    opportunities: list[Opportunity]
