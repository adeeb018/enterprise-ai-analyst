# import json

# # from src.llm.llm_client import CloudLLMClient
# from src.llm.gemini_client import GeminiLLMClient
# from src.llm.llm_client import CloudLLMClient
# from src.pipeline.query_pipeline import QueryPipeline
# from src.sql.engine import SQLEngine
# from src.sql.enums import SQLStatus
# from src.sql.executor.executor import SQLExecutor
# from src.sql.generator.builder import SchemaContextBuilder
# from src.sql.generator.prompt_builder import PromptBuilder
# from src.sql.models import SQLCandidate
# from src.sql.repair import repair_engine
# from src.sql.validator.validator import SQLValidator
# from src.utils.helper import get_graph, parse_llm_json

# text = "Show diabetic patients admitted to ICU"

# def main():

#     pipeline = QueryPipeline()

#     while True:
#         question = input("\nQuestion: ")
#         if question.lower() in {
#             "quit",
#             "exit",
#         }:
#             break

#         retrieval_result = pipeline.retrieve_schema(
#             text
#         )

#         print("\n" + "=" * 80)
#         print("RANKED TABLES")
#         print("=" * 80)

#         for table in retrieval_result.ranked_context.ranked_tables:

#             print(
#                 f"{table.score:.3f}"
#                 f"  "
#                 f"{table.node.node.id}"
#             )

#             for evidence in table.evidence:
#                 print(f"      • {evidence}")


#         # builder = PromptBuilder()
#         schema_context_builder=SchemaContextBuilder()
#         schema_context = schema_context_builder.build(retrieval_result)

        # prompt = builder.build(
        #     text,
        #     retrieval_result.plan,
        #     schema_context,
        # )

        # print(prompt)

        # sql_agent = GeminiLLMClient()
        # response = sql_agent.generate(prompt=prompt, format='json')
        # print(response)
        # response_dict = parse_llm_json(response)

        # response_dict = {
        #     "sql": "SELECT DISTINCT p.subject_id, p.gender, p.anchor_age, p.dod FROM mimiciv_hosp.patients p INNER JOIN mimiciv_icu.icustays i ON p.subject_id = i.subject_id INNER JOIN mimiciv_hosp.diagnoses_icd d ON p.subject_id = d.subject_id AND i.hadm_id = d.hadm_id INNER JOIN mimiciv_hosp.d_icd_diagnoses di ON d.icd_code = di.icd_code AND d.icd_version = di.icd_version WHERE di.long_title ILIKE '%diabetes%'",
        #     "explanation": "The query retrieves patients who have a diagnosis of diabetes (resolved using diagnoses_icd and d_icd_diagnoses with an ILIKE '%diabetes%' filter) and were admitted to the ICU (by joining the icustays table)."
        #     }
        # # print(response_dict['sql'])
        # validator = SQLValidator()
        # sqlCandidate = SQLCandidate(sql=response_dict['sql'],
        #                             explanation=response_dict['explanation'])
        # report = validator.validate(candidate=sqlCandidate,
        #                             schema_context=schema_context,
        #                             graph=get_graph())
        
        # print(report)
        # repair_sql = repair_engine.RepairEngine()
        
        # if not report.is_valid:
        #     repair_result = repair_sql.repair(
        #         question=text,
        #         candidate=sqlCandidate,
        #         report=report,
        #         schema_context=schema_context,
        #         validator = validator,
        #         graph = get_graph()
        #     )

        #     sqlCandidate.sql = repair_result.sql
        # print("repair done\n",sqlCandidate)

        # sql_engine = SQLEngine()
        # candidate = sql_engine.generate(
        #     plan=retrieval_result.plan,
        #     question=question,
        #     schema_context=schema_context,
        #     graph=get_graph(),
        # )
        # print("final result",candidate)
#         sql_candidate = SQLCandidate(sql="SELECT DISTINCT p.subject_id, p.gender, p.anchor_age, p.dod, i.stay_id, i.intime, i.outtime FROM mimiciv_hosp.patients p INNER JOIN mimiciv_icu.icustays i ON p.subject_id = i.subject_id INNER JOIN mimiciv_hosp.admissions a ON i.hadm_id = a.hadm_id INNER JOIN mimiciv_hosp.diagnoses_icd d ON a.hadm_id = d.hadm_id INNER JOIN mimiciv_hosp.d_icd_diagnoses di ON d.icd_code = di.icd_code AND d.icd_version = di.icd_version WHERE di.long_title ILIKE '%diabetes%'", explanation='Replaced invalid direct join between icustays and diagnoses_icd with a join through the admissions table, using the existing foreign key relationships: icustays.hadm_id -> admissions.hadm_id and diagnoses_icd.hadm_id -> admissions.hadm_id.', status=SQLStatus.GENERATED)

#         # final result sql="SELECT DISTINCT p.subject_id, p.gender, p.anchor_age, p.dod, i.stay_id, i.intime, i.outtime FROM mimiciv_hosp.patients p INNER JOIN mimiciv_icu.icustays i ON p.subject_id = i.subject_id INNER JOIN mimiciv_hosp.admissions a ON i.hadm_id = a.hadm_id INNER JOIN mimiciv_hosp.diagnoses_icd d ON a.hadm_id = d.hadm_id INNER JOIN mimiciv_hosp.d_icd_diagnoses di ON d.icd_code = di.icd_code AND d.icd_version = di.icd_version WHERE di.long_title ILIKE '%diabetes%'" explanation='Replaced invalid direct join between icustays and diagnoses_icd with a join through the admissions table, using the existing foreign key relationships: icustays.hadm_id -> admissions.hadm_id and diagnoses_icd.hadm_id -> admissions.hadm_id.' status=<SQLStatus.GENERATED: 'generated'>
#         executor = SQLExecutor()

#         result = executor.execute(sql_candidate)


#         print(result.columns)
#         print(result.rows)


# if __name__ == "__main__":
#     main()

# from src.pipeline.query_pipeline import QueryPipeline
# from src.utils.helper import parse_llm_json

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

#         sql_agent = GeminiLLMClient()
#         response = sql_agent.generate(prompt=prompt, format='json')
#         print(response)

#         response_dict = parse_llm_json(response)
#         # print(response_dict['sql'])
#         validator = SQLValidator()
#         sqlCandidate = SQLCandidate(sql=response_dict['sql'],
#                                     explanation=response_dict['explanation'])
#         report = validator.validate(candidate=sqlCandidate, schema_context=schema_context,graph=get_graph())
#         print(report)

# if __name__ == "__main__":
#     main()


# from pathlib import Path

# from src.agent.analyst import AnalystAgent
# from src.config.paths import TEST_DIRECTORY
# from src.evaluation.recorder import RunRecorder
# from src.evaluation.replay import RunReplay

# def main():

#     agent = AnalystAgent()

#     question = "Show diabetic patients admitted to ICU."

#     # result = agent.query(
#     #     "Show diabetic patients admitted to ICU."
#     # )

#     # print(result.columns)
#     # print(result.rows)

#     recorder = RunRecorder(output_dir=TEST_DIRECTORY)

#     run = agent.query(question)

#     recorder.save(run, "test.json")

#     loaded = RunReplay.load(Path(TEST_DIRECTORY/"test.json"))

#     # assert run.question == loaded.question

#     # assert run.generated_sql.sql == loaded.generated_sql.sql

#     # assert run.execution_result.rows == loaded.execution_result.rows

#     print("RUN ROWS:", repr(run.execution_result.rows))
#     print("LOADED ROWS:", repr(loaded.execution_result.rows))

#     assert run.execution_result.rows == loaded.execution_result.rows

#     assert run.schema_context == loaded.schema_context

# if __name__ == "__main__":
#     main()

from pathlib import Path

from src.agent.analyst import AnalystAgent
from src.config.paths import TEST_DIRECTORY
from src.evaluation.dataset import BenchmarkDataset
from src.evaluation.loader import RunLoader
from src.evaluation.recorder import RunRecorder
from src.evaluation.replay import ReplayEngine
from src.evaluation.runner import BenchmarkRunner


def main():
    # dataset = BenchmarkDataset.from_questions(
    #     [
    #         "Show diabetic patients admitted to ICU.",
    #         "Average glucose level by age group.",
    #     ]
    # )

    benchmark_file = Path(TEST_DIRECTORY/"dataset/mimiciv_demo.json")
    dataset = BenchmarkDataset.from_json(benchmark_file)

    agent = AnalystAgent()
    recorder = RunRecorder(output_dir=TEST_DIRECTORY)

    runner = BenchmarkRunner(
        agent,
        recorder,
    )

    runner.run(dataset)
    print("Benchmark run completed successfully.")

    # loader = RunLoader()
    # run = loader.load(TEST_DIRECTORY/"001.json")

    # replay = ReplayEngine(agent)

    # # result = replay.replay_execution(run)
    # retrieval = replay.replay_retrieval(
    #     run.question
    # )
    # print(retrieval.plan)
    # replay.replay_sql_generation(run)
    # replay.replay_schema_context(run.retrieval_result)
    # replay.replay_retrieval(run.question)


if __name__ == "__main__":
    main()