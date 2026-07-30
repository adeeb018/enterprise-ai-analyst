from pathlib import Path

from src.evaluation.models import AgentRun


class RunLoader:

    @staticmethod
    def load(
        path: str | Path,
    ) -> AgentRun:

        return AgentRun.model_validate_json(
            Path(path).read_text()
        )