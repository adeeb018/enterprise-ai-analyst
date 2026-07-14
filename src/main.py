from src.planner.planner import Planner
from src.retrieval.retriever import Retriever

from src.pipeline.query_pipeline import QueryPipeline

retriever = Retriever()

text = "Show diabetic patients admitted to ICU"

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

if __name__ == "__main__":
    main()