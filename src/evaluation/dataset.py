import json
from pathlib import Path

from src.evaluation.models import BenchmarkQuestion


class BenchmarkDataset:

    def __init__(
        self,
        questions: list[BenchmarkQuestion],
    ):
        self._questions = questions

    @classmethod
    def from_json(
        cls,
        path: str | Path,
    ) -> "BenchmarkDataset":
        path = Path(path)
        raw_data = json.loads(path.read_text(encoding="utf-8"))
        
        # Parses each dictionary from the JSON into a BenchmarkQuestion model
        questions = [BenchmarkQuestion(**item) for item in raw_data]
        return cls(questions)

    @classmethod
    def from_questions(
        cls,
        questions: list[str],
    ):

        return cls(
            [
                BenchmarkQuestion(
                    id=f"{i:03}",
                    question=question,
                )
                for i, question in enumerate(questions, start=1)
            ]
        )

    def __iter__(self):

        return iter(self._questions)

    def __len__(self):

        return len(self._questions)