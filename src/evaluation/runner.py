from src.agent.analyst import AnalystAgent
from src.evaluation.dataset import BenchmarkDataset
from src.evaluation.recorder import RunRecorder


class BenchmarkRunner:

    def __init__(
        self,
        agent: AnalystAgent,
        recorder: RunRecorder,
    ):

        self._agent = agent
        self._recorder = recorder

    def run(
        self,
        dataset: BenchmarkDataset,
    ):

        for benchmark in dataset:

            run = self._agent.query(
                benchmark.question
            )

            self._recorder.save(
                run=run,
                filename=f"{benchmark.id}.json",
            )