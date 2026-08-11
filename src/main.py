

from pathlib import Path
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

    recorder = RunRecorder(output_dir=TEST_DIRECTORY)

    runner = BenchmarkRunner(
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


# from src.agent.analyst import AnalystAgent
# from src.orchestration.langgraph.graph import build_graph

# graph = build_graph()

# agent = AnalystAgent()

# result = graph.invoke(
#     {
#         "question": "Find the maximum lab value for creatinine for ICU admissions"
#     },
#     # config={
#     #     "configurable": {
#     #         "agent": agent,
#     #     }
#     # },
# )
# print(result["run"].generated_sql)
# print(result["run"].error)
# print(result["run"].answer)

