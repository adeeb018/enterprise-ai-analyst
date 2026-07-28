from textwrap import dedent

from src.sql.generator.models import SchemaContext
from src.sql.repair.models import RepairPlan


class RepairPromptBuilder:
    """
    Builds the repair prompt sent to the LLM.
    """

    def _format_schema(self, schema_context: SchemaContext) -> str:
        """Converts the SchemaContext object into a readable text format for the LLM."""
        lines = []

        lines.append("### Tables and Columns:")
        for t in schema_context.tables:
            lines.append(f"- Table: {t.schema_name}.{t.table}")
            if t.description:
                lines.append(f"  Description: {t.description}")
            
            lines.append("  Columns:")
            for col in t.columns:
                pk_tag = " [PRIMARY KEY]" if col.name in t.primary_keys else ""
                lines.append(f"    - {col.name} ({col.data_type}){pk_tag}")
            
            if t.foreign_keys:
                lines.append("  Foreign Keys:")
                for fk in t.foreign_keys:
                    lines.append(f"    - {fk.column} -> {fk.referred_schema}.{fk.referred_table}({fk.referred_column})")
            lines.append("")

        if schema_context.relationships:
            lines.append("### Valid Relationships:")
            for rel in schema_context.relationships:
                lines.append(f"- {rel.source_schema}.{rel.source_table}.{rel.source_column} = {rel.target_schema}.{rel.target_table}.{rel.target_column}")

        return "\n".join(lines)

    def build(
        self,
        plan: RepairPlan,
        schema_context: SchemaContext
    ) -> str:

        issues = []

        for index, instruction in enumerate(plan.instructions, start=1):

            issue = f"{index}. {instruction.message}"

            if instruction.location:
                issue += f"\n   Location: {instruction.location}"

            if instruction.suggestion:
                issue += (
                    f"\n   Suggestion: {instruction.suggestion}"
                )

            issues.append(issue)

        issue_text = "\n\n".join(issues)
        formatted_schema = self._format_schema(schema_context)

        return dedent(
            f"""
            You are repairing a PostgreSQL SQL query.

            ## User Question

            {plan.question}

            ## Database Schema
            {formatted_schema}

            ## Original SQL

            ```sql
            {plan.original_sql}
            ```

            ## Validation Errors

            {issue_text}

            ## Instructions

            - Fix ONLY the reported validation errors.
            - Preserve all correct parts of the query.
            - Do not change the query intent.
            - Do not invent tables or columns.
            - Use only the provided schema.
            - Return only the corrected SQL.
            - Do not include explanations.
            
            ## Output Format

            You must return a valid JSON object matching this exact structure, with no markdown formatting or extra text outside the JSON:
            {{
              "sql": "YOUR_CORRECTED_SQL_QUERY_HERE"
            }}
            """
        ).strip()