from src.planner.planner_models import QueryPlan

from .models import SchemaContext


def _format_columns(cols) -> str:
    """Safely format column fields whether they are strings or lists."""
    if isinstance(cols, list):
        return ", ".join(cols)
    return str(cols)


class PromptBuilder:
    """
    Builds the complete prompt for SQL generation.
    """

    SYSTEM_PROMPT = """
    You are an expert PostgreSQL SQL engineer working ONLY from the schema and
    relationship information provided in this context. You have zero prior
    knowledge of the underlying database.

    SCHEMA & INVENTION RULES
    - Use ONLY the tables, columns, and relationships provided in this context.
    - Never invent a table, column, data type, or relationship that isn't
    explicitly present in the provided schema or Relationships section.
    - If a table is referenced in the Relationships section, it exists and can
    be joined — even if its column list is abbreviated there. Abbreviated
    does NOT mean unavailable.

    SCHEMA QUALIFICATION
    - Always fully qualify every table name with the schema prefix EXACTLY as
    it appears in the provided schema or Relationships section
    (e.g. mimiciv_hosp.patients, mimiciv_icu.icustays).
    - If a table's prefix is abbreviated in the Relationships section, use the
    prefix given there — do not guess, infer, or omit it.
    - If a table you need has no prefix given anywhere in the provided context,
    that is missing information: apply the REFUSAL CONDITION below. Do not
    guess a prefix from general knowledge of MIMIC-IV or any other database.

    JOIN GRAIN
    - Respect the grain of each table based on its provided primary/foreign
    keys. Never join a parent-level entity (e.g. a patient demographic
    table keyed on subject_id only) using a child-level identifier
    (e.g. hadm_id, stay_id) that isn't actually a column on that table.
    Check the provided column list before adding a join condition — do not
    add columns to a join that aren't listed for that table.
    - Use foreign key relationships when joining tables. Prefer explicit JOIN
    syntax over implicit joins or subqueries where a JOIN is equivalent.

    RESOLVING CONDITIONS, CONCEPTS, AND TERMS
    - You will often need to resolve a user's plain-language term (e.g. a
    condition, drug, or lab test name) to a code stored in a dictionary or
    lookup table (e.g. d_icd_diagnoses, d_items, d_labitems). This is
    expected and is NOT a reason to refuse.
    - When a dictionary/lookup table is present in the provided schema, resolve
    the term by matching against its descriptive text column using
    ILIKE '%term%' — do not require the exact code to be given to you in
    advance. This applies consistently to every query, not selectively.
    - Only treat a concept as unresolvable if the dictionary/lookup table
    itself is genuinely absent from the provided schema — not merely because
    the specific code value isn't spelled out in the prompt.

    REFUSAL CONDITION
    - If, and only if, the tables or columns required are genuinely absent
    from the provided schema and Relationships section (not just abbreviated,
    and not just missing a specific data value that ILIKE resolution can
    reach), set "sql" to an empty string ("") and explain precisely which
    table or column is missing and why it's required.
    - Before refusing, double-check: is there a dictionary/lookup table
    provided that would let you resolve this via ILIKE instead? If yes,
    do not refuse — use it.
    - Apply this threshold consistently across all queries in a session; do
    not refuse one query for a reason (e.g. "no exact code given") that a
    structurally similar query in the same session was answered without.

    OUTPUT
    - Generate valid, executable PostgreSQL SQL only.
    - Return ONLY valid JSON. Do not wrap the JSON in markdown code blocks.
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

            source_cols = _format_columns(relationship.source_column)
            target_cols = _format_columns(relationship.target_column)

            lines.append(
                (
                    f"- "
                    f"{relationship.source_schema}."
                    f"{relationship.source_table}."
                    f"({source_cols})"

                    f" -> "

                    f"{relationship.target_schema}."
                    f"{relationship.target_table}."
                    f"({target_cols})"
                )
            )

        return "\n".join(lines)