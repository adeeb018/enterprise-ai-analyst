from src.sql.models import AnswerResult, ExecutionResult, SQLCandidate, SQLPlan, ValidationIssue, ValidationReport
from src.sql.enums import ExecutionStatus, ValidationIssueType

def main():
    # issue = ValidationIssue(
    #     issue_type=ValidationIssueType.MISSING_COLUMN,
    #     message="Column subject_id not found."
    # )

    # print(issue)

    # plan = SQLPlan(
    #     objective="Count diabetic ICU patients",
    #     tables=["patients", "diagnoses_icd", "icustays"],
    #     filters=["Diagnosis = Diabetes"],
    #     aggregations=["COUNT"],
    # )

    # print(plan.model_dump())

    # candidate = SQLCandidate(
    #     sql="SELECT * FROM mimiciv_hosp.patients",
    #     explanation="Retrieve all patients.",
    # )

    # print(candidate.model_dump())
    # report = ValidationReport(
    #     issues=[
    #         ValidationIssue(
    #             issue_type=ValidationIssueType.MISSING_COLUMN,
    #             message="subject not found",
    #         )
    #     ],
    #     validator_name="SchemaValidator",
    # )

    # print(report.is_valid)
    # print(report.error_count)
    # print(report.warning_count)

    # result = ExecutionResult(
    #     status=ExecutionStatus.SUCCESS,
    #     rows=[
    #         {
    #             "subject_id": 1001,
    #             "gender": "M"
    #         },
    #         {
    #             "subject_id": 1002,
    #             "gender": "F"
    #         }
    #     ],
    #     columns=[
    #         "subject_id",
    #         "gender"
    #     ],
    #     execution_time_ms=18.4
    # )

    # print(result.row_count)
    answer = AnswerResult(
        answer="There were 42 diabetic patients admitted to the ICU.",
        reasoning=(
            "Counted ICU admissions for patients with a diabetes diagnosis."
        ),
    )

    print(answer.model_dump())

if __name__ == '__main__':
    main()
