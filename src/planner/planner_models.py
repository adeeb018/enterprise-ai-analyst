from pydantic import BaseModel


class QueryPlan(BaseModel):

    objective: str

    concepts: list[str]

    constraints: list[str]

    output: str