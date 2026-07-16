from src.pipeline.query_pipeline import QueryPipeline

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
            text
        )

        print("\n" + "=" * 80)
        print("RANKED TABLES")
        print("=" * 80)

        for table in result.ranked_context.ranked_tables:

            print(
                f"{table.score:.3f}"
                f"  "
                f"{table.node.node.id}"
            )

            for evidence in table.evidence:
                print(f"      • {evidence}")


if __name__ == "__main__":
    main()