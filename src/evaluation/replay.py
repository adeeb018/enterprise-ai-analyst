from pathlib import Path

from src.evaluation.models import AgentRun


class RunReplay:

    @staticmethod
    def load(path: Path) -> AgentRun:

        return AgentRun.model_validate_json(
            path.read_text(encoding="utf-8")
        )