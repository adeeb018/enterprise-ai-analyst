from pydantic import BaseModel

from src.retrieval.query_models import RetrievedChunk
from src.planner.planner_models import QueryPlan


class PipelineResult(BaseModel):
    plan: QueryPlan
    retrieved_tables: list[RetrievedChunk]