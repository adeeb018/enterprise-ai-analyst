import json

from src.config.paths import ENRICHED_SCHEMA_JSON, GRAPH_JSON
from src.graph.graph_loader import GraphLoader
from src.ingestion.schema_models import TableInfo
from src.pipeline.pipeline_models import PipelineResult
from src.planner.planner import Planner
from src.planner.planner_models import QueryPlan
from src.retrieval.context_ranker import ContextRanker
from src.retrieval.graph_expander import GraphExpander
from src.retrieval.query_models import RetrievedChunk
from src.retrieval.retriever import Retriever


class QueryPipeline:

    def __init__(self):

        self.planner = Planner()
        self.retriever = Retriever()
        self.expander = self._build_expander()
        self.ranker = ContextRanker()

    def _build_expander(
        self,
    ) -> GraphExpander:

        schema = [
            TableInfo.model_validate(item)
            for item in json.loads(
                ENRICHED_SCHEMA_JSON.read_text()
            )
        ]

        graph = GraphLoader().load(
            graph_path=GRAPH_JSON,
            schema=schema,
        )

        return GraphExpander(graph)

    def retrieve_schema(
        self,
        question: str,
        top_k: int = 4,
    ) -> PipelineResult:

        plan = self.planner.plan(question)
        plan = QueryPlan.model_validate(plan)

        all_results: list[RetrievedChunk] = []

        seen_tables = set()

        for concept in plan.concepts:

            print(f"\nSearching for concept: {concept}")

            results = self.retriever.retrieve(
                concept,
                limit=top_k,
            )

            print(f"\nResults for concept: {concept}")

            for r in results:
                print(
                    f"{r.score:.4f} "
                    f"{r.schema_name}.{r.table}"
                )

            for result in results:

                table_id = (
                    f"{result.schema_name}.{result.table}"
                )

                if table_id in seen_tables:
                    continue

                seen_tables.add(table_id)

                all_results.append(result)

        all_results.sort(
            key=lambda x: x.score,
            reverse=True,
        )

        expanded_context = self.expander.expand(
            retrieved_tables=all_results,
        )

        ranked_context = self.ranker.rank(
            expanded_context
        )

        return PipelineResult(
            plan=plan,
            retrieved_tables=all_results,
            expanded_context=expanded_context,
            ranked_context= ranked_context
        )