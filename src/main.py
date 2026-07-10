from src.retrieval.retriever import Retriever

retriever = Retriever()

text = "Show diabetic patients admitted to ICU"


def main():

    retriever = Retriever()

    while True:

        question = input("\nQuestion: ")

        if question.lower() in {"exit", "quit"}:
            break

        results = retriever.retrieve(question)

        for result in results:
            print(f"\nScore: {result.score:.4f}")
            print(f"{result.schema_name}.{result.table}")
            print(f"Keywords: {', '.join(result.keywords)}")
            print("-" * 60)

if __name__ == "__main__":
    main()