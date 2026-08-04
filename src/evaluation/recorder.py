import json
from pathlib import Path

from src.evaluation.models import AgentRun


class RunRecorder:

    def __init__(self, output_dir: Path):

        self._output_dir = output_dir
        self._output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        run: AgentRun,
        filename: str,
    ) -> None:

        path = self._output_dir / filename

        with path.open(
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                run.model_dump(mode="json"),
                f,
                indent=2,
                ensure_ascii=False,
            )