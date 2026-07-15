from pydantic import BaseModel

from src.retrieval.query_models import RetrievedChunk
from src.planner.planner_models import QueryPlan
from src.retrieval.ranking_models import RankedContext
from src.retrieval.retrieval_models import ExpandedContext


class PipelineResult(BaseModel):
    plan: QueryPlan
    retrieved_tables: list[RetrievedChunk]
    expanded_context: ExpandedContext
    ranked_context: RankedContext