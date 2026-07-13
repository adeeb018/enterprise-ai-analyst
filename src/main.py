from src.planner.planner import Planner
from src.retrieval.retriever import Retriever

from src.pipeline.query_pipeline import QueryPipeline

retriever = Retriever()

text = "Show diabetic patients admitted to ICU"


# def main():

#     retriever = Retriever()

#     while True:

#         question = input("\nQuestion: ")

#         if question.lower() in {"exit", "quit"}:
#             break

#         results = retriever.retrieve(question)

#         for result in results:
#             print(f"\nScore: {result.score:.4f}")
#             print(f"{result.schema_name}.{result.table}")
#             print(f"Keywords: {', '.join(result.keywords)}")
#             print("-" * 60)

def main():

    pipeline = QueryPipeline()

    while True:
        question = input("\nQuestion: ")
        if question.lower() in {
            "quit",
            "exit",
        }:
            break

        result = pipeline.retrieve_schema(
            question
        )

        # print("\nQuery Plan")
        # print("=" * 60)
        # print(
        #     result.plan.model_dump_json(
        #         indent=2,
        #     )
        # )
        # print("\nRetrieved Tables")
        # print("=" * 60)
        # for table in result.retrieved_tables:
        #     print(
        #         f"{table.score:.4f}"
        #     )
        #     print(
        #         f"{table.schema_name}.{table.table}"
        #     )
        #     print(
        #         f"{', '.join(table.keywords)}"
        #     )
        #     print("-" * 60)

if __name__ == "__main__":
    main()