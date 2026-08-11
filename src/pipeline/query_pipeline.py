import json

from src.graph.graph_loader import GraphLoader
from src.graph.schema_graph import SchemaGraph
from src.ingestion.schema_models import TableInfo
from src.pipeline.failure_analyzer import FailureAnalyzer
from src.pipeline.pipeline_models import RetrievalResult
from src.planner.planner import Planner
from src.planner.planner_models import QueryPlan
from src.retrieval.ranking.context_ranker import ContextRanker
from src.retrieval.graph_expander import GraphExpander
from src.retrieval.query_models import RetrievedChunk
from src.retrieval.retriever import Retriever
from src.sql.generator.models import SchemaContext
from src.sql.models import ValidationReport
from src.utils.helper import get_graph
from concurrent.futures import ThreadPoolExecutor, as_completed


class QueryPipeline:

    def __init__(self):

        self.planner = Planner()
        self.retriever = Retriever()
        self.graph = get_graph()
        self.expander = GraphExpander(graph=self.graph)
        self.ranker = ContextRanker(graph=self.graph)
        self._failure_analyzer = FailureAnalyzer()

    def retrieve_schema(
        self,
        question: str,
        top_k: int = 2,
    ) -> RetrievalResult:

        plan = self.planner.plan(question)
        plan = QueryPlan.model_validate(plan)

        all_results: list[RetrievedChunk] = []
        seen_tables = set()

        def _search(concept: str):
            return self.retriever.retrieve(concept, limit=top_k)

        with ThreadPoolExecutor(max_workers=min(len(plan.concepts), 8)) as executor:
            futures = [executor.submit(_search, concept) for concept in plan.concepts]

            for future in as_completed(futures):
                results = future.result()

                for result in results:
                    table_id = f"{result.schema_name}.{result.table}"
                    if table_id in seen_tables:
                        continue
                    seen_tables.add(table_id)
                    all_results.append(result)

        all_results.sort(key=lambda x: x.score, reverse=True)

        return self._process_retrieval(
            plan=plan,
            question=question,
            retrieved_tables=all_results,
        )


    # def retrieve_schema(
    #     self,
    #     question: str,
    #     top_k: int = 2,
    # ) -> RetrievalResult:

    #     plan = self.planner.plan(question)
    #     plan = QueryPlan.model_validate(plan)

    #     all_results: list[RetrievedChunk] = []

    #     seen_tables = set()

    #     for concept in plan.concepts:

    #         print(f"\nSearching for concept: {concept}")

    #         results = self.retriever.retrieve(
    #             concept,
    #             limit=top_k,
    #         )

    #         print(f"\nResults for concept: {concept}")

    #         for r in results:
    #             print(
    #                 f"{r.score:.4f} "
    #                 f"{r.schema_name}.{r.table}"
    #             )

    #         for result in results:

    #             table_id = (
    #                 f"{result.schema_name}.{result.table}"
    #             )

    #             if table_id in seen_tables:
    #                 continue

    #             seen_tables.add(table_id)

    #             all_results.append(result)

    #     all_results.sort(
    #         key=lambda x: x.score,
    #         reverse=True,
    #     )

    #     return self._process_retrieval(
    #         plan=plan,
    #         question=question,
    #         retrieved_tables=all_results,
    #     )

    def _process_retrieval(
        self,
        *,
        plan: QueryPlan,
        question: str,
        retrieved_tables: list[RetrievedChunk],
    ) -> RetrievalResult:

        expanded_context = self.expander.expand(
            retrieved_tables=retrieved_tables,
        )

        ranked_context = self.ranker.rank(
            expanded_context,
            query=question,
        )

        return RetrievalResult(
            plan=plan,
            retrieved_tables=retrieved_tables,
            expanded_context=expanded_context,
            ranked_context=ranked_context,
        )

    def retrieve_more_schema(
        self,
        *,
        question: str,
        retrieval_result: RetrievalResult,
        validation_report: ValidationReport,
        top_k: int = 2,
    ) -> RetrievalResult:
        
        hints = self._failure_analyzer.analyze(
            validation_report
        )

        additional_results = []

        seen = {
            f"{r.schema_name}.{r.table}"
            for r in retrieval_result.retrieved_tables
        }

        for hint in hints:

            results = self.retriever.retrieve(
                hint,
                limit=top_k,
            )

            for result in results:

                table_id = (
                    f"{result.schema_name}.{result.table}"
                )

                if table_id in seen:
                    continue

                seen.add(table_id)

                additional_results.append(result)

        merged_results = (
            retrieval_result.retrieved_tables
            + additional_results
        )

        merged_results.sort(
            key=lambda r: r.score,
            reverse=True,
        )

        return self._process_retrieval(
            plan=retrieval_result.plan,
            question=question,
            retrieved_tables=merged_results,
        )
