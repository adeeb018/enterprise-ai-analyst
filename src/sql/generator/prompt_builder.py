from src.planner.planner_models import QueryPlan

from .models import SchemaContext


class PromptBuilder:
    """
    Builds the complete prompt for SQL generation.
    """

    SYSTEM_PROMPT = """
You are an expert PostgreSQL SQL engineer.

Your task is to generate syntactically correct PostgreSQL SQL.

Rules:

- Use ONLY the provided schema.
- Never invent tables.
- Never invent columns.
- Use foreign key relationships when joining tables.
- Prefer explicit JOIN syntax.
- Return ONLY valid JSON.
"""

    OUTPUT_FORMAT = """
Return ONLY JSON.

{
    "sql": "...",
    "explanation": "..."
}
"""

    def build(
        self,
        question: str,
        plan: QueryPlan,
        schema_context: SchemaContext,
    ) -> str:

        prompt = []

        prompt.append(self.SYSTEM_PROMPT.strip())

        prompt.append(self._question(question))

        prompt.append(self._plan(plan))

        prompt.append(self._schema(schema_context))

        prompt.append(self.OUTPUT_FORMAT.strip())

        return "\n\n".join(prompt)
    
    def _question(  
        self,
        question: str,
    ) -> str:

        return f"""## User Question
                {question}
                """
    
    def _plan(
        self,
        plan: QueryPlan,
    ) -> str:

        concepts = "\n".join(
            f"- {concept}"
            for concept in plan.concepts
        )

        constraints = "\n".join(
            f"- {constraint}"
            for constraint in plan.constraints
        )

        return f"""
                    ## Query Plan

                    Objective:
                    {plan.objective}

                    Concepts:
                    {concepts}

                    Constraints:
                    {constraints}

                    Expected Output:
                    {plan.output}
                """
    

    def _schema(
        self,
        context: SchemaContext,
    ) -> str:

        sections = [
            "## Database Schema"
        ]

        sections.append(
            self._tables(context)
        )

        sections.append(
            self._relationships(context)
        )

        return "\n\n".join(sections)
    

    def _tables(
        self,
        context: SchemaContext,
    ) -> str:

        lines = [
            "### Relevant Tables"
        ]

        for table in context.tables:

            lines.append(
                f"\nTable: {table.schema}.{table.name}"
            )

            if table.description:
                lines.append(
                    f"Description: {table.description}"
                )

            lines.append("Columns:")

            for column in table.columns:

                flags = []

                if column.is_primary_key:
                    flags.append("PK")

                if column.is_foreign_key:
                    flags.append("FK")

                suffix = ""

                if flags:
                    suffix = f" ({', '.join(flags)})"

                lines.append(
                    f"- {column.name}{suffix}"
                )

        return "\n".join(lines)
    

    def _relationships(
        self,
        context: SchemaContext,
    ) -> str:

        lines = [
            "### Relationships"
        ]

        for relationship in context.relationships:

            lines.append(
                (
                    f"- "
                    f"{relationship.source_schema}."
                    f"{relationship.source_table}."
                    f"{relationship.source_column}"

                    f" -> "

                    f"{relationship.target_schema}."
                    f"{relationship.target_table}."
                    f"{relationship.target_column}"
                )
            )

        return "\n".join(lines)