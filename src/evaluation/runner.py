from src.agent.analyst import AnalystAgent
from src.evaluation.dataset import BenchmarkDataset
from src.evaluation.recorder import RunRecorder
from src.orchestration.langgraph.graph import build_graph


class BenchmarkRunner:

    def __init__(
        self,
        recorder: RunRecorder,
    ):
        self._recorder = recorder
        self._lgraph =  build_graph()
    def run(
        self,
        dataset: BenchmarkDataset,
    ):

        for i,benchmark in enumerate(dataset):

            if(i<11):
                continue

            # run = self._agent.query(
            #     benchmark.question
            # )

            state = self._lgraph.invoke(
                {
                    "question": benchmark.question,
                },
            )
            run =  state["run"]

            self._recorder.save(
                run=run,
                filename=f"{benchmark.id}.json",
            )