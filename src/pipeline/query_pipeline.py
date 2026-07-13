from src.pipeline.pipeline_models import PipelineResult
from src.planner.planner import Planner
from src.planner.planner_models import QueryPlan
from src.retrieval.query_models import RetrievedChunk
from src.retrieval.retriever import Retriever


class QueryPipeline:

    def __init__(self):

        self.planner = Planner()
        self.retriever = Retriever()

    def retrieve_schema(
        self,
        question: str,
        top_k: int = 10,
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

        return PipelineResult(
            plan=plan,
            retrieved_tables=all_results,
        )