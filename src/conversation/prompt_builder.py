class QuestionRewritePromptBuilder:

    def build(
        self,
        *,
        question: str,
        history: str,
    ) -> str:

        if not history:

            return f"""
You are a question rewriting component for an
enterprise database analyst.

There is no conversation history.

Return the user's question unchanged.

User question:
{question}

Return ONLY the standalone question.
"""

        return f"""
You are a question rewriting component for an
enterprise database analyst.

Your job is to convert the user's latest question
into a standalone question that can be understood
without the conversation history.

Conversation history:
{history}

Latest user question:
{question}

Rules:

1. Resolve references such as:
   "they", "them", "those", "these", "it", "that",
   "the patients", "the admissions", etc.

2. Preserve the user's intended meaning.

3. Do not answer the question.

4. Do not add facts that are not present in the
   conversation.

5. Do not change requested filters, conditions,
   entities, dates, or metrics.

6. If the latest question is already standalone,
   return it unchanged.

7. Return ONLY the rewritten standalone question.

Standalone question:
"""