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
    - Use ONLY the provided schema and explicit relationships.
    - Never invent tables, columns, or data types.
    - If a table is referenced in the Relationships section, it exists and can be joined, even if its detailed column list is abbreviated.
    - Do NOT use any prior knowledge of MIMIC-IV, medical databases, or standard enterprise schemas.
    - If the requested information CANNOT be obtained using the provided tables and relationships, you must NOT invent SQL. Instead, set the "sql" field to an empty string ("") and provide a clear explanation in the "explanation" field.
    - Use foreign key relationships when joining tables.
    - Prefer explicit JOIN syntax.
    - Generate valid, executable PostgreSQL SQL only.
    - Return ONLY valid JSON. Do not wrap the JSON in markdown code blocks (like ```json).
    """

    OUTPUT_FORMAT = """
    Return ONLY valid JSON using the exact structure below:
    {
        "sql": "YOUR_SQL_QUERY_HERE_OR_EMPTY_STRING",
        "explanation": "YOUR_EXPLANATION_HERE"
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

        return f"""## Query Plan

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
            "## Database Schema",
            self._primary_tables(context),
            self._tables(context),
            self._relationships(context),
        ]

        return "\n\n".join(sections)
    
    def _primary_tables(
        self,
        context: SchemaContext,
    ) -> str:

        lines = [
            "## Primary Tables"
        ]

        for table in context.primary_tables:
            lines.append(
                f"- {table.schema}.{table.table}"
            )

        return "\n".join(lines)
    

    def _tables(
        self,
        context: SchemaContext,
    ) -> str:

        lines = [
            "### Relevant Tables"
        ]

        for table in context.tables:

            lines.append(
                f"\nTable: {table.schema_name}.{table.table}"
            )

            if table.description:
                lines.append(
                    f"Description: {table.description}"
                )

            lines.append("Columns:")

            foreign_key_columns = {
                fk.column
                for fk in table.foreign_keys
            }

            for column in table.columns:

                flags = []

                if column.name in table.primary_keys:
                    flags.append("PK")

                if column.name in foreign_key_columns:
                    flags.append("FK")

                if not column.nullable:
                    flags.append("NOT NULL")

                suffix = ""

                if flags:
                    suffix = f" ({', '.join(flags)})"

                lines.append(
                    f"- {column.name}: {column.data_type}{suffix}"
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