from src.llm.gemini_client import GeminiLLMClient
from src.llm.llm_client import CloudLLMClient
from src.planner.planner_models import QueryPlan
from src.sql.generator.prompt_builder import PromptBuilder
from src.sql.models import SQLCandidate
from src.utils.helper import parse_llm_json


class SQLGenerator:
    """
    Generates SQL from a natural language question.

        Question
            ↓
      PromptBuilder
            ↓
            LLM
            ↓
      SQLCandidate
    """

    def __init__(self):

        self._prompt_builder = PromptBuilder()
        self._llm = GeminiLLMClient()

    def generate(
        self,
        *,
        plan: QueryPlan,
        question: str,
        schema_context,
    ) -> SQLCandidate:

        prompt = self._prompt_builder.build(
            plan=plan,
            question=question,
            schema_context=schema_context,
        )

        response = self._llm.generate(
            prompt=prompt,
            format="json",
        )

        result = parse_llm_json(response)
        # print("result1",result["sql"])
        # print("explanation",result.get("explanation"))

        # return SQLCandidate(sql="SELECT MAX(le.valuenum) AS max_creatinine FROM mimiciv_hosp.labevents le INNER JOIN mimiciv_hosp.d_labitems dl ON le.itemid = dl.itemid INNER JOIN mimiciv_icu.icustays ie ON le.subject_id = ie.subject_id AND le.hadm_id = ie.hadm_id WHERE dl.label ILIKE '%creatinine%'",
        #              explanation="This query finds the maximum creatinine lab value for ICU admissions by joining the labevents table with the d_labitems table (to filter for creatinine using ILIKE) and the icustays table (to restrict the results to ICU admissions via subject_id and hadm_id)")

        return SQLCandidate(
            sql=result["sql"],
            explanation=result.get("explanation"),
        )