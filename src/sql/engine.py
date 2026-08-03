from src.planner.planner_models import QueryPlan
from src.sql.exceptions import SQLGenerationError
from src.sql.generator.generator import SQLGenerator
from src.sql.models import SQLCandidate
from src.sql.repair.repair_engine import RepairEngine
from src.sql.validator.validator import SQLValidator


class SQLEngine:

    MAX_REPAIR_ATTEMPTS = 2

    def __init__(self):

        self._generator = SQLGenerator()
        self._validator = SQLValidator()
        self._repair_engine = RepairEngine()


    def generate_candidate(
        self,
        *,
        plan: QueryPlan,
        question: str,
        schema_context,
    ) -> SQLCandidate:

        return self._generator.generate(
            plan=plan,
            question=question,
            schema_context=schema_context,
        )
    
    def validate_candidate(
        self,
        *,
        candidate: SQLCandidate,
        schema_context,
        graph,
    ):

        return self._validator.validate(
            candidate=candidate,
            schema_context=schema_context,
            graph=graph,
        )
    
    def repair_candidate(
        self,
        *,
        question: str,
        candidate: SQLCandidate,
        report,
        schema_context,
    ):

        return self._repair_engine.repair(
            question=question,
            candidate=candidate,
            report=report,
            schema_context=schema_context,
        )

    def generate(
        self,
        *,
        plan: QueryPlan,
        question: str,
        schema_context,
        graph,
    ) -> SQLCandidate:

        candidate = self._generator.generate(
            plan=plan,
            question=question,
            schema_context=schema_context,
        )
        print(candidate)

        for _ in range(self.MAX_REPAIR_ATTEMPTS + 1):

            report = self._validator.validate(
                candidate=candidate,
                schema_context=schema_context,
                graph=graph,
            )

            if report.is_valid:
                return candidate

            candidate = self._repair_engine.repair(
                question=question,
                candidate=candidate,
                report=report,
                schema_context=schema_context,
            )

        raise SQLGenerationError(
            f"Unable to generate a valid SQL after "
            f"{self.MAX_REPAIR_ATTEMPTS} repair attempts."
        )