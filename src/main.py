import json

from src.llm.llm_client import CloudLLMClient
from src.pipeline.query_pipeline import QueryPipeline
from src.sql.generator.builder import SchemaContextBuilder
from src.sql.generator.prompt_builder import PromptBuilder

text = "Find the average heart rate of patients with sepsis"

def main():

    pipeline = QueryPipeline()

    while True:
        question = input("\nQuestion: ")
        if question.lower() in {
            "quit",
            "exit",
        }:
            break

        retrieval_result = pipeline.retrieve_schema(
            text
        )

        # print("\n" + "=" * 80)
        # print("RANKED TABLES")
        # print("=" * 80)

        # for table in retrieval_result.ranked_context.ranked_tables:

        #     print(
        #         f"{table.score:.3f}"
        #         f"  "
        #         f"{table.node.node.id}"
        #     )

        #     for evidence in table.evidence:
        #         print(f"      • {evidence}")


        builder = PromptBuilder()
        schema_context_builder=SchemaContextBuilder()
        schema_context = schema_context_builder.build(retrieval_result)

        prompt = builder.build(
            text,
            retrieval_result.plan,
            schema_context,
        )

        print(prompt)

        sql_agent = CloudLLMClient()
        response = sql_agent.generate(prompt=prompt, format='json')
        print(response)
        response_dict = json.loads(response)
        print(response_dict['sql'])


if __name__ == "__main__":
    main()

# from src.pipeline.query_pipeline import QueryPipeline

# # 10 Diverse Test Queries covering different relational paths in MIMIC-IV
# TEST_QUERIES = [
#     "Show diabetic patients admitted to ICU",
#     "Find the average heart rate of patients with sepsis",
#     "List female patients over 65 years old admitted to the emergency department",
#     "Show patients who underwent coronary artery bypass graft surgery",
#     "Find the maximum lab value for creatinine for ICU admissions",
#     "List prescriptions given to patients diagnosed with pneumonia",
#     "Show patients who had fluid output recorded during their ICU stay",
#     "Find the mortality rate of patients admitted with myocardial infarction",
#     "List microbiology culture results for septic shock patients",
#     "Show demographic details and length of stay for ICU patients"
# ]

# def main():
#     pipeline = QueryPipeline()

#     print(f"\n🚀 Running automated test suite of {len(TEST_QUERIES)} queries...\n")

#     for i, question in enumerate(TEST_QUERIES, 1):
#         print("=" * 80)
#         print(f"TEST QUERY {i}/{len(TEST_QUERIES)}: {question}")
#         print("=" * 80)

#         retrieval_result = pipeline.retrieve_schema(question)

#         # print("\nRANKED TABLES OUTPUT:")
#         # for table in result.ranked_context.ranked_tables:
#         #     print(
#         #         f"{table.score:.3f}  "
#         #         f"{table.node.node.id}"
#         #     )
#         #     for evidence in table.evidence:
#         #         print(f"      • {evidence}")
#         # print("\n" + "-" * 80 + "\n")
#         builder = PromptBuilder()
#         schema_context_builder=SchemaContextBuilder()
#         schema_context = schema_context_builder.build(retrieval_result)

#         prompt = builder.build(
#             question,
#             retrieval_result.plan,
#             schema_context,
#         )

#         # print(prompt)

#         sql_agent = CloudLLMClient()
#         response = sql_agent.generate(prompt=prompt)
#         print(response)

# if __name__ == "__main__":
#     main()